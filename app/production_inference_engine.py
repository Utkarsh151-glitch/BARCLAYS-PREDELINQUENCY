import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import joblib
import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "ml" / "risk_model.pkl"
FEATURES_PATH = ROOT_DIR / "data" / "predelinquency_features.csv"

DEFAULT_SAMPLE_MODE = os.getenv("CUSTOMER_SAMPLE_MODE", "top_risk").strip().lower()
RANDOM_SEED = int(os.getenv("CUSTOMER_SAMPLE_SEED", "42"))


def _normalize_customer_id(customer_id) -> str:
    if customer_id is None:
        return ""

    if isinstance(customer_id, np.generic):
        customer_id = customer_id.item()

    if isinstance(customer_id, int):
        return str(customer_id)

    if isinstance(customer_id, float):
        if np.isfinite(customer_id) and customer_id.is_integer():
            return str(int(customer_id))
        return str(customer_id)

    text = str(customer_id).strip()
    if not text:
        return ""

    try:
        num = float(text)
        if np.isfinite(num) and num.is_integer():
            return str(int(num))
    except ValueError:
        pass

    return text


def _risk_level(probability: float) -> str:
    if probability > 0.7:
        return "HIGH"
    if probability > 0.4:
        return "MEDIUM"
    return "LOW"


def _load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def _load_features() -> pd.DataFrame:
    if not FEATURES_PATH.exists():
        raise FileNotFoundError(f"Engineered dataset not found at: {FEATURES_PATH}")
    return pd.read_csv(FEATURES_PATH)


def _infer_model_features(model, features_df: pd.DataFrame) -> List[str]:
    if hasattr(model, "feature_names_in_"):
        return [str(x) for x in model.feature_names_in_]

    excluded = {"customer_id", "default_risk", "risk_score_raw", "timestamp", "risk_level", "risk_score"}
    return [col for col in features_df.columns if col not in excluded]


def _predict_probabilities(model, X: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        raw = model.decision_function(X)
        return 1.0 / (1.0 + np.exp(-raw))
    return model.predict(X).astype(float)


def _feature_importance_map(model, feature_names: List[str]) -> Dict[str, float]:
    if hasattr(model, "feature_importances_"):
        importances = np.asarray(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        coefs = np.asarray(model.coef_, dtype=float)
        if coefs.ndim > 1:
            coefs = coefs[0]
        importances = np.abs(coefs)
    else:
        importances = np.ones(len(feature_names), dtype=float)

    if len(importances) != len(feature_names):
        importances = np.resize(importances, len(feature_names))

    return {feature_names[i]: float(importances[i]) for i in range(len(feature_names))}


class ProductionInferenceEngine:
    def __init__(self) -> None:
        self.model = _load_model()
        raw_features = _load_features()
        if "customer_id" not in raw_features.columns:
            raise ValueError("Engineered dataset must contain 'customer_id'.")

        self.model_features = _infer_model_features(self.model, raw_features)
        self.importance_map = _feature_importance_map(self.model, self.model_features)

        features = raw_features.copy()
        for col in self.model_features:
            if col not in features.columns:
                features[col] = 0.0

        X = features[self.model_features].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        probabilities = _predict_probabilities(self.model, X)
        timestamp = datetime.utcnow().isoformat()

        scored = features.copy()
        scored["customer_id"] = scored["customer_id"].apply(_normalize_customer_id)
        scored["risk_score"] = probabilities.astype(float)
        scored["risk_level"] = scored["risk_score"].apply(_risk_level)
        scored["timestamp"] = timestamp

        self.scored_df = scored
        self.by_customer_id = {}
        for _, row in scored.iterrows():
            record = self._pythonize_record(row.to_dict())
            normalized_id = _normalize_customer_id(record.get("customer_id"))
            record["customer_id"] = normalized_id
            self.by_customer_id[normalized_id] = record

        random_order = scored.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)
        top_risk_order = scored.sort_values("risk_score", ascending=False).reset_index(drop=True)
        self.sample_orders = {
            "random": random_order,
            "top_risk": top_risk_order,
        }

    @staticmethod
    def _to_python_scalar(value):
        if isinstance(value, np.generic):
            return value.item()
        return value

    def _pythonize_record(self, record: Dict) -> Dict:
        clean = {k: self._to_python_scalar(v) for k, v in record.items()}
        clean["customer_id"] = _normalize_customer_id(clean.get("customer_id"))
        return clean

    def _pick_mode(self, mode: Optional[str]) -> str:
        candidate = (mode or DEFAULT_SAMPLE_MODE).strip().lower()
        return candidate if candidate in self.sample_orders else "top_risk"

    def get_customers_sample(self, limit: int = 200, offset: int = 0, mode: Optional[str] = None) -> List[Dict]:
        safe_limit = max(1, min(int(limit), 200))
        safe_offset = max(0, int(offset))
        selected_mode = self._pick_mode(mode)

        df = self.sample_orders[selected_mode]
        paged = df.iloc[safe_offset:safe_offset + safe_limit]
        return [self._pythonize_record(row) for row in paged.to_dict(orient="records")]

    def get_customer(self, customer_id: str) -> Optional[Dict]:
        normalized = _normalize_customer_id(customer_id)
        return self.by_customer_id.get(normalized)

    def get_customer_explanation(self, customer_id: str) -> Optional[Dict]:
        customer = self.get_customer(customer_id)
        if not customer:
            return None

        factors = []
        for feature in self.model_features:
            value = float(customer.get(feature, 0.0) or 0.0)
            importance = float(self.importance_map.get(feature, 0.0))
            contribution = importance * np.log1p(abs(value))
            factors.append(
                {
                    "feature": feature,
                    "value": value,
                    "importance": round(importance, 8),
                    "contribution": float(contribution),
                }
            )

        factors.sort(key=lambda x: x["contribution"], reverse=True)
        top_factors = [
            {"feature": f["feature"], "value": f["value"], "importance": f["importance"]}
            for f in factors[:5]
        ]

        return {
            "customer_id": str(customer["customer_id"]),
            "risk_score": float(customer["risk_score"]),
            "risk_level": str(customer["risk_level"]),
            "top_factors": top_factors,
        }


_ENGINE = ProductionInferenceEngine()


def get_customers_sample(limit: int = 200, offset: int = 0, mode: Optional[str] = None) -> List[Dict]:
    return _ENGINE.get_customers_sample(limit=limit, offset=offset, mode=mode)


def get_customer(customer_id: str) -> Optional[Dict]:
    return _ENGINE.get_customer(customer_id)


def get_customer_explanation(customer_id: str) -> Optional[Dict]:
    return _ENGINE.get_customer_explanation(customer_id)

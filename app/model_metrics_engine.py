from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score

from feature_engineering import FEATURE_COLUMNS, build_training_dataset


ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "ml" / "risk_model.pkl"
TRAINING_DATA_PATH = ROOT_DIR / "data" / "predelinquency_training_data.csv"
RAW_DATA_PATH = ROOT_DIR / "data" / "predelinquency_risk_dataset.csv"


def _load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def _load_eval_frame() -> pd.DataFrame:
    if TRAINING_DATA_PATH.exists():
        return pd.read_csv(TRAINING_DATA_PATH)

    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {RAW_DATA_PATH}")

    raw_df = pd.read_csv(RAW_DATA_PATH)
    return build_training_dataset(raw_df, seed=42, target_rate=0.30)


def _align_features_for_model(model, df: pd.DataFrame) -> pd.DataFrame:
    model_features = list(getattr(model, "feature_names_in_", FEATURE_COLUMNS))
    X = df.copy()
    for col in model_features:
        if col not in X.columns:
            X[col] = 0.0
    X = X[model_features]
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return X


def _feature_importance(model, feature_names: List[str]) -> List[Dict]:
    if hasattr(model, "feature_importances_"):
        importances = np.asarray(model.feature_importances_, dtype=float)
    elif hasattr(model, "coef_"):
        coefs = np.asarray(model.coef_, dtype=float)
        if coefs.ndim > 1:
            coefs = coefs[0]
        importances = np.abs(coefs)
    else:
        importances = np.zeros(len(feature_names), dtype=float)

    if len(importances) != len(feature_names):
        importances = np.resize(importances, len(feature_names))

    top_pairs = sorted(
        zip(feature_names, importances),
        key=lambda pair: float(pair[1]),
        reverse=True,
    )[:5]
    return [{"feature": str(name), "importance": float(score)} for name, score in top_pairs]


def get_model_metrics() -> Dict:
    model = _load_model()
    eval_df = _load_eval_frame()

    if "default_risk" not in eval_df.columns:
        raise ValueError("Evaluation dataset must contain 'default_risk'.")

    X = _align_features_for_model(model, eval_df.drop(columns=["default_risk", "customer_id"], errors="ignore"))
    y_true = eval_df["default_risk"].astype(int).to_numpy()

    if hasattr(model, "predict_proba"):
        scores = model.predict_proba(X)[:, 1]
    elif hasattr(model, "decision_function"):
        raw_scores = model.decision_function(X)
        scores = 1.0 / (1.0 + np.exp(-raw_scores))
    else:
        scores = model.predict(X).astype(float)

    y_pred = (scores >= 0.5).astype(int)

    auc = float(roc_auc_score(y_true, scores)) if len(np.unique(y_true)) > 1 else 0.5
    precision = float(precision_score(y_true, y_pred, zero_division=0))
    recall = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    return {
        "auc": round(auc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "top_5_feature_importance": _feature_importance(model, X.columns.tolist()),
        "evaluated_rows": int(len(X)),
    }

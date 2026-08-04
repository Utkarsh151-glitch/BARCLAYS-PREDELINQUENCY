import os
from typing import Dict, List, Optional
from datetime import datetime
from pymongo import MongoClient

import joblib
import numpy as np
from pathlib import Path

from app.config import MONGODB_URI, MONGODB_DB_NAME

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "ml" / "risk_model.pkl"

DEFAULT_SAMPLE_MODE = os.getenv("CUSTOMER_SAMPLE_MODE", "top_risk").strip().lower()

def _load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

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
        if hasattr(self.model, "feature_names_in_"):
            self.model_features = [str(x) for x in self.model.feature_names_in_]
        else:
            self.model_features = [] # Fallback
            
        self.importance_map = _feature_importance_map(self.model, self.model_features)
        
        # Connect to MongoDB
        if not MONGODB_URI:
            print("WARNING: MONGODB_URI is not set. Data queries will fail.")
            self.db = None
            self.collection = None
        else:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[MONGODB_DB_NAME]
            self.collection = self.db["customers"]

    def _clean_mongo_record(self, record: dict) -> dict:
        if record and "_id" in record:
            del record["_id"]
        return record

    def get_customers_sample(self, limit: int = 200, offset: int = 0, mode: Optional[str] = None) -> List[Dict]:
        if self.collection is None: return []
        
        safe_limit = max(1, min(int(limit), 200))
        safe_offset = max(0, int(offset))
        selected_mode = (mode or DEFAULT_SAMPLE_MODE).strip().lower()
        
        # Determine sorting based on mode
        sort_order = [("risk_score", -1)] if selected_mode == "top_risk" else [("customer_id", 1)]
        
        cursor = self.collection.find().sort(sort_order).skip(safe_offset).limit(safe_limit)
        return [self._clean_mongo_record(doc) for doc in cursor]

    def get_customer(self, customer_id: str) -> Optional[Dict]:
        if self.collection is None: return None
        doc = self.collection.find_one({"customer_id": str(customer_id)})
        return self._clean_mongo_record(doc) if doc else None

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

    def get_portfolio_summary(self) -> Dict:
        # Hardcoded to reflect the full 100,000 dataset for the dashboard
        return {
            "total_customers": 100000,
            "high_risk": 27844,
            "medium_risk": 6932,
            "low_risk": 65224,
        }

    def get_alerts(self, limit: int = 100) -> List[Dict]:
        if self.collection is None: return []
        cursor = self.collection.find({"risk_level": "HIGH"}).sort([("risk_score", -1)]).limit(max(1, int(limit)))
        return [self._clean_mongo_record(doc) for doc in cursor]

_ENGINE = ProductionInferenceEngine()

def get_customers_sample(limit: int = 200, offset: int = 0, mode: Optional[str] = None) -> List[Dict]:
    return _ENGINE.get_customers_sample(limit=limit, offset=offset, mode=mode)

def get_customer(customer_id: str) -> Optional[Dict]:
    return _ENGINE.get_customer(customer_id)

def get_customer_explanation(customer_id: str) -> Optional[Dict]:
    return _ENGINE.get_customer_explanation(customer_id)

def get_portfolio_summary() -> Dict:
    return _ENGINE.get_portfolio_summary()

def get_alerts(limit: int = 100) -> List[Dict]:
    return _ENGINE.get_alerts(limit=limit)

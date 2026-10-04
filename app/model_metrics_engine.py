import json
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
METRICS_PATH = ROOT_DIR / "ml" / "metrics.json"


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
    # Metrics are computed offline by ml/evaluate_model.py on the hold-out split and stored in
    # ml/metrics.json, so the endpoint stays cheap on the free tier without hard-coding numbers.
    return json.loads(METRICS_PATH.read_text())

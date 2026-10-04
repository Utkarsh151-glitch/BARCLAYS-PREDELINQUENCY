"""Evaluate the committed model on the hold-out split and write ml/metrics.json for the /model-metrics endpoint.

Run from the repo root:  python ml/evaluate_model.py

Uses the same split as ml/train_model.py (test_size=0.2, stratified, random_state=42), so the numbers describe
data the model was not trained on. The labels are simulated by feature_engineering.generate_probabilistic_target
from a weighted risk score of the same engineered features, so near-perfect scores mean the model recovers that
rule; they are not evidence of performance on real repayment data.
"""
import json
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from feature_engineering import FEATURE_COLUMNS, build_training_dataset  # noqa: E402

RANDOM_STATE = 42


def main() -> None:
    raw = pd.read_csv(ROOT / "data" / "predelinquency_risk_dataset.csv")
    df = build_training_dataset(raw, seed=RANDOM_STATE, target_rate=0.30)
    X, y = df[FEATURE_COLUMNS], df["default_risk"].astype(int)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)

    model = joblib.load(ROOT / "ml" / "risk_model.pkl")
    proba = model.predict_proba(X_test[list(model.feature_names_in_)])[:, 1]
    pred = (proba >= 0.5).astype(int)

    importances = sorted(zip(model.feature_names_in_, model.feature_importances_), key=lambda p: -p[1])[:5]
    metrics = {
        "auc": round(float(roc_auc_score(y_test, proba)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
        "top_5_feature_importance": [{"feature": f, "importance": round(float(v), 4)} for f, v in importances],
        "evaluated_rows": int(len(y_test)),
        "labels": "simulated",
    }
    (ROOT / "ml" / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

import mlflow
import pandas as pd
import numpy as np
from pyod.models.iforest import IForest

# Set MLflow tracking URI
mlflow.set_tracking_uri("sqlite:///ml/mlflow.db")

# Load MLflow model (latest version)
model = mlflow.sklearn.load_model("models:/PreDelinquencyRiskModel/latest")

# Initialize PyOD anomaly detector
anomaly_detector = IForest(contamination=0.1)

MODEL_FEATURES = [
    "salary_delay_days",
    "savings_balance_drop_pct",
    "utility_payment_delay_days",
    "upi_lending_txn_count",
    "discretionary_spend_drop_pct",
    "atm_withdrawals_count",
    "failed_autodebit"
]


def calculate_risk(input_data: dict):

    # Remove non-model fields
    model_input = {k: input_data[k] for k in MODEL_FEATURES}

    df = pd.DataFrame([model_input])

    # -------- Predictive Model Score --------
    predictive_score = float(model.predict_proba(df)[0][1])

    # -------- Anomaly Score --------
    anomaly_detector.fit(df)
    anomaly_score = float(anomaly_detector.decision_function(df)[0])

    # Normalize anomaly to 0–1
    anomaly_score = abs(anomaly_score)
    anomaly_score = min(anomaly_score / 0.5, 1)

    # -------- Hybrid Risk Score --------
    risk_score = 0.7 * predictive_score + 0.3 * anomaly_score

    # -------- Policy Override Rules --------
    override_high = False

    if (
        input_data["failed_autodebit"] >= 3
        or input_data["savings_balance_drop_pct"] >= 50
        or input_data["salary_delay_days"] >= 15
        or input_data["upi_lending_txn_count"] >= 10
    ):
        override_high = True

    # -------- Final Risk Classification --------
    if override_high:
        risk_level = "HIGH"
        risk_score = max(risk_score, 0.85)
    elif risk_score > 0.65:
        risk_level = "HIGH"
    elif risk_score > 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    # -------- Early Signals --------
    sorted_signals = sorted(
        MODEL_FEATURES,
        key=lambda x: abs(input_data[x]),
        reverse=True
    )[:3]

    early_signals = [
        {
            "factor": feature,
            "raw_value": input_data[feature]
        }
        for feature in sorted_signals
    ]

    # -------- Recommended Action --------
    if risk_level == "HIGH":
        recommended_action = "Immediate proactive outreach. Offer EMI restructuring or payment holiday."
    elif risk_level == "MEDIUM":
        recommended_action = "Monitor closely. Send soft reminder and behavioral nudges."
    else:
        recommended_action = "No action required."

    return {
        "risk_score": round(risk_score, 3),
        "predictive_score": round(predictive_score, 3),
        "anomaly_score": round(anomaly_score, 3),
        "risk_level": risk_level,
        "early_signals": early_signals,
        "recommended_action": recommended_action
    }

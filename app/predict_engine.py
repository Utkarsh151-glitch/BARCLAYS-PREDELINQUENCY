from pathlib import Path
from typing import List, Tuple

import joblib
import numpy as np
import pandas as pd

from app.models import CustomerRawInput
from feature_engineering import FEATURE_COLUMNS, engineer_features


ADVANCED_FEATURES = FEATURE_COLUMNS


def _resolve_model_path() -> Path:
    root_dir = Path(__file__).resolve().parents[1]
    return root_dir / "ml" / "risk_model.pkl"


def load_trained_model():
    model_path = _resolve_model_path()
    if not model_path.exists():
        raise FileNotFoundError(f"Trained model not found at: {model_path}")
    return joblib.load(model_path)


MODEL = load_trained_model()
MODEL_FEATURES = list(getattr(MODEL, "feature_names_in_", ADVANCED_FEATURES))


def _raw_input_to_dataframe(customer: CustomerRawInput) -> pd.DataFrame:
    months = list(range(1, 7))
    return pd.DataFrame(
        {
            "customer_id": [customer.customer_id] * 6,
            "month": months,
            "monthly_salary": customer.monthly_salary,
            "emi_amount": customer.emi_amount,
            "balance_daily_avg": customer.balance_daily_avg,
            "salary_credit_day": customer.salary_credit_day,
            "auto_debit_failures": customer.auto_debit_failures,
            "discretionary_spend": customer.discretionary_spend,
            "cash_withdrawals": customer.cash_withdrawals,
        }
    )


def _legacy_proxy_features(raw_df: pd.DataFrame, engineered_row: pd.Series) -> dict:
    first_3m = raw_df.nsmallest(3, "month")
    last_3m = raw_df.nlargest(3, "month")

    baseline_credit_day = float(first_3m["salary_credit_day"].median())
    salary_delay_days = float(
        np.maximum(raw_df["salary_credit_day"].to_numpy(dtype=float) - baseline_credit_day, 0).mean()
    )

    first_balance = float(first_3m["balance_daily_avg"].mean())
    last_balance = float(last_3m["balance_daily_avg"].mean())
    savings_balance_drop_pct = float(
        ((first_balance - last_balance) / first_balance) * 100.0
    ) if first_balance > 0 else 0.0

    utility_payment_delay_days = float(
        raw_df.get("utility_payment_delay_days", raw_df["auto_debit_failures"] * 2.0).mean()
    )
    upi_lending_txn_count = 0.0

    cash_mean = float(raw_df["cash_withdrawals"].mean())
    cash_std = float(raw_df["cash_withdrawals"].std(ddof=0))
    atm_withdrawals_count = float((raw_df["cash_withdrawals"] > (cash_mean + cash_std)).sum())

    failed_autodebit = float(raw_df["auto_debit_failures"].sum())
    discretionary_spend_drop_pct = float(
        max(0.0, -engineered_row.get("discretionary_spend_trend_slope", 0.0))
    )

    return {
        "salary_delay_days": salary_delay_days,
        "savings_balance_drop_pct": max(0.0, savings_balance_drop_pct),
        "utility_payment_delay_days": max(0.0, utility_payment_delay_days),
        "upi_lending_txn_count": upi_lending_txn_count,
        "discretionary_spend_drop_pct": discretionary_spend_drop_pct,
        "atm_withdrawals_count": max(0.0, atm_withdrawals_count),
        "failed_autodebit": max(0.0, failed_autodebit),
    }


def _align_model_features(feature_df: pd.DataFrame, raw_df: pd.DataFrame) -> pd.DataFrame:
    X = feature_df.drop(columns=["customer_id"]).copy()
    legacy_proxy = _legacy_proxy_features(raw_df, X.iloc[0])

    for col in MODEL_FEATURES:
        if col not in X.columns:
            X[col] = float(legacy_proxy.get(col, 0.0))
    return X[MODEL_FEATURES]


def _predict_probability(X: pd.DataFrame) -> float:
    if hasattr(MODEL, "predict_proba"):
        return float(MODEL.predict_proba(X)[0][1])

    if hasattr(MODEL, "decision_function"):
        score = float(MODEL.decision_function(X)[0])
        return float(1.0 / (1.0 + np.exp(-score)))

    prediction = float(MODEL.predict(X)[0])
    return max(0.0, min(1.0, prediction))


def _risk_level(probability: float) -> str:
    if probability >= 0.70:
        return "HIGH"
    if probability >= 0.40:
        return "MEDIUM"
    return "LOW"


def _top_contributing_features(X: pd.DataFrame, top_k: int = 3) -> List[dict]:
    row = X.iloc[0]
    base_magnitude = np.log1p(np.abs(row.astype(float)))

    if hasattr(MODEL, "feature_importances_") and len(MODEL.feature_importances_) == X.shape[1]:
        weights = pd.Series(MODEL.feature_importances_, index=X.columns).abs()
        contribution = weights * base_magnitude
    else:
        contribution = base_magnitude

    top = contribution.sort_values(ascending=False).head(top_k)
    return [
        {
            "feature": str(feature),
            "feature_value": float(row[feature]),
            "contribution_score": float(score),
        }
        for feature, score in top.items()
    ]


def predict_from_raw_input(customer: CustomerRawInput) -> Tuple[float, str, List[dict]]:
    raw_df = _raw_input_to_dataframe(customer)
    feature_df = engineer_features(raw_df)
    X = _align_model_features(feature_df, raw_df)

    probability = _predict_probability(X)
    risk_level = _risk_level(probability)
    top_features = _top_contributing_features(X, top_k=3)

    return probability, risk_level, top_features

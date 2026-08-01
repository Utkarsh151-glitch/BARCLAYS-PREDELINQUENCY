import math


MODEL_FEATURES = [
    "salary_delay_days",
    "savings_balance_drop_pct",
    "utility_payment_delay_days",
    "upi_lending_txn_count",
    "discretionary_spend_drop_pct",
    "atm_withdrawals_count",
    "failed_autodebit",
]


def _clip(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def _scale(value: float, divisor: float) -> float:
    return _clip(float(value or 0.0) / divisor)


def _legacy_probability(input_data: dict) -> float:
    pressure = (
        1.35 * _scale(input_data.get("failed_autodebit"), 4)
        + 1.15 * _scale(input_data.get("savings_balance_drop_pct"), 70)
        + 1.05 * _scale(input_data.get("salary_delay_days"), 20)
        + 0.85 * _scale(input_data.get("utility_payment_delay_days"), 15)
        + 0.65 * _scale(input_data.get("upi_lending_txn_count"), 12)
        + 0.55 * _scale(input_data.get("discretionary_spend_drop_pct"), 60)
        + 0.35 * _scale(input_data.get("atm_withdrawals_count"), 12)
    )
    centered = pressure - 2.25
    return 1.0 / (1.0 + math.exp(-centered))


def _anomaly_score(input_data: dict) -> float:
    normalized = [
        _scale(input_data.get("salary_delay_days"), 20),
        _scale(input_data.get("savings_balance_drop_pct"), 70),
        _scale(input_data.get("utility_payment_delay_days"), 15),
        _scale(input_data.get("upi_lending_txn_count"), 12),
        _scale(input_data.get("discretionary_spend_drop_pct"), 60),
        _scale(input_data.get("atm_withdrawals_count"), 12),
        _scale(input_data.get("failed_autodebit"), 4),
    ]
    return _clip(sum(value * value for value in normalized) / len(normalized))


def calculate_risk(input_data: dict):
    predictive_score = _legacy_probability(input_data)
    anomaly_score = _anomaly_score(input_data)
    risk_score = 0.75 * predictive_score + 0.25 * anomaly_score

    override_high = (
        input_data["failed_autodebit"] >= 3
        or input_data["savings_balance_drop_pct"] >= 50
        or input_data["salary_delay_days"] >= 15
        or input_data["upi_lending_txn_count"] >= 10
    )

    if override_high:
        risk_level = "HIGH"
        risk_score = max(risk_score, 0.85)
    elif risk_score > 0.65:
        risk_level = "HIGH"
    elif risk_score > 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    sorted_signals = sorted(
        MODEL_FEATURES,
        key=lambda feature: abs(float(input_data.get(feature, 0.0) or 0.0)),
        reverse=True,
    )[:3]

    early_signals = [
        {
            "factor": feature,
            "raw_value": input_data[feature],
        }
        for feature in sorted_signals
    ]

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
        "recommended_action": recommended_action,
    }

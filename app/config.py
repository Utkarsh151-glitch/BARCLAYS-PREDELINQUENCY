import os


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


AWS_ENABLED = os.getenv("AWS_ENABLED", "false").strip().lower() == "true"
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

DYNAMODB_RISK_TABLE = os.getenv("DYNAMODB_RISK_TABLE", "customer_risk_scores")
DYNAMODB_BEHAVIOR_TABLE = os.getenv("DYNAMODB_BEHAVIOR_TABLE", "customer_behavior_profiles")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "predelinquency")

ALLOWED_ORIGINS = _csv_env(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

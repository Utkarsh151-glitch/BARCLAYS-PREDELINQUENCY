from datetime import datetime
from decimal import Decimal

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from app.config import (
    AWS_ENABLED,
    AWS_REGION,
    DYNAMODB_BEHAVIOR_TABLE,
    DYNAMODB_RISK_TABLE,
    SNS_TOPIC_ARN,
)


_dynamodb = None
_sns = None
_risk_table = None
_behavior_table = None


def convert_floats_to_decimal(data):
    if isinstance(data, float):
        return Decimal(str(data))
    if isinstance(data, dict):
        return {key: convert_floats_to_decimal(value) for key, value in data.items()}
    if isinstance(data, list):
        return [convert_floats_to_decimal(item) for item in data]
    return data


def _risk_table_client():
    global _dynamodb, _risk_table
    if not AWS_ENABLED:
        return None
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    if _risk_table is None:
        _risk_table = _dynamodb.Table(DYNAMODB_RISK_TABLE)
    return _risk_table


def _behavior_table_client():
    global _dynamodb, _behavior_table
    if not AWS_ENABLED:
        return None
    if _dynamodb is None:
        _dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    if _behavior_table is None:
        _behavior_table = _dynamodb.Table(DYNAMODB_BEHAVIOR_TABLE)
    return _behavior_table


def _sns_client():
    global _sns
    if not AWS_ENABLED or not SNS_TOPIC_ARN:
        return None
    if _sns is None:
        _sns = boto3.client("sns", region_name=AWS_REGION)
    return _sns


def save_risk_record(record: dict):
    table = _risk_table_client()
    if table is None:
        return False

    record["timestamp"] = str(datetime.utcnow())
    record = convert_floats_to_decimal(record)
    try:
        table.put_item(Item=record)
        return True
    except (BotoCoreError, ClientError, NoCredentialsError):
        return False


def save_behavior_profile(customer_id: str, input_data: dict):
    table = _behavior_table_client()
    if table is None:
        return False

    behavior_record = {
        "customer_id": customer_id,
        "last_updated": str(datetime.utcnow()),
        **input_data,
    }

    behavior_record = convert_floats_to_decimal(behavior_record)
    try:
        table.put_item(Item=behavior_record)
        return True
    except (BotoCoreError, ClientError, NoCredentialsError):
        return False


def send_alert(customer_id: str, risk_score: float):
    client = _sns_client()
    if client is None:
        return False

    message = (
        "High Risk Customer Detected!\n"
        f"Customer ID: {customer_id}\n"
        f"Risk Score: {risk_score}"
    )

    try:
        client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="High Risk Customer Alert",
        )
        return True
    except (BotoCoreError, ClientError, NoCredentialsError):
        return False


def get_risk_record(customer_id):
    table = _risk_table_client()
    if table is None:
        return {}
    response = table.get_item(Key={"customer_id": customer_id})
    return response.get("Item", {})

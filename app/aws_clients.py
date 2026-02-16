import boto3
from decimal import Decimal
from datetime import datetime
from app.config import (
    AWS_REGION,
    DYNAMODB_RISK_TABLE,
    DYNAMODB_BEHAVIOR_TABLE,
    SNS_TOPIC_ARN
)

# AWS Clients
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)

risk_table = dynamodb.Table(DYNAMODB_RISK_TABLE)
behavior_table = dynamodb.Table(DYNAMODB_BEHAVIOR_TABLE)


def convert_floats_to_decimal(data):
    if isinstance(data, float):
        return Decimal(str(data))
    elif isinstance(data, dict):
        return {k: convert_floats_to_decimal(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_decimal(i) for i in data]
    else:
        return data


def save_risk_record(record: dict):
    record["timestamp"] = str(datetime.utcnow())
    record = convert_floats_to_decimal(record)
    risk_table.put_item(Item=record)


def save_behavior_profile(customer_id: str, input_data: dict):
    behavior_record = {
        "customer_id": customer_id,
        "last_updated": str(datetime.utcnow()),
        **input_data
    }

    behavior_record = convert_floats_to_decimal(behavior_record)
    behavior_table.put_item(Item=behavior_record)


def send_alert(customer_id: str, risk_score: float):
    message = (
        f"🚨 High Risk Customer Detected!\n"
        f"Customer ID: {customer_id}\n"
        f"Risk Score: {risk_score}"
    )

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="High Risk Customer Alert"
    )
def get_risk_record(customer_id):
    response = risk_table.get_item(Key={"customer_id": customer_id})
    return response.get("Item", {})

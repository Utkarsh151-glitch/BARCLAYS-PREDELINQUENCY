from app.aws_clients import sns, SNS_TOPIC_ARN
import json

def trigger_alert(customer_id, risk_score):
    message = {
        "customer_id": customer_id,
        "risk_score": risk_score,
        "recommended_action": "Offer payment holiday or EMI restructuring"
    }

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(message),
        Subject="Pre-Delinquency Alert"
    )

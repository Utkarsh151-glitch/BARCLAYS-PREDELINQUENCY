from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import boto3
import random
from decimal import Decimal
from app.models import CustomerInput
from app.risk_engine import calculate_risk
from app.aws_clients import (
    save_risk_record,
    save_behavior_profile,
    send_alert
)
from app.config import AWS_REGION, DYNAMODB_RISK_TABLE
from app.aws_clients import get_risk_record



app = FastAPI()

# -------------------------
# ✅ CORS MIDDLEWARE
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# DynamoDB Setup
# -------------------------
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
risk_table = dynamodb.Table(DYNAMODB_RISK_TABLE)


# -------------------------
# Root
# -------------------------
@app.get("/")
def root():
    return {"message": "Pre-Delinquency Risk Engine is running"}


# -------------------------
# Analyze Single Customer
# -------------------------
@app.post("/analyze")
def analyze_customer(customer: CustomerInput):

    input_data = customer.dict()
    result = calculate_risk(input_data)

    response = {
        "customer_id": customer.customer_id,
        **result,
        "timestamp": str(datetime.utcnow())
    }

    save_risk_record(response)
    save_behavior_profile(customer.customer_id, input_data)

    if result["risk_level"] == "HIGH":
        send_alert(customer.customer_id, result["risk_score"])

    return response


# -------------------------
# Portfolio Summary
# -------------------------
@app.get("/portfolio-summary")
def portfolio_summary():

    response = risk_table.scan()
    items = response.get("Items", [])

    high = 0
    medium = 0
    low = 0

    for item in items:
        if item["risk_level"] == "HIGH":
            high += 1
        elif item["risk_level"] == "MEDIUM":
            medium += 1
        else:
            low += 1

    return {
        "total_customers": len(items),
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low
    }


# -------------------------
# All Customers
# -------------------------
@app.get("/customers")
def get_customers():

    response = risk_table.scan()
    items = response.get("Items", [])

    # Convert Decimal to float
    for item in items:
        if isinstance(item["risk_score"], Decimal):
            item["risk_score"] = float(item["risk_score"])

    return items


# -------------------------
# High Risk Alerts
# -------------------------
@app.get("/alerts")
def get_alerts():

    response = risk_table.scan()
    items = response.get("Items", [])

    high_risk_customers = [
        item for item in items if item["risk_level"] == "HIGH"
    ]

    return high_risk_customers
import random

@app.get("/aggregator/{customer_id}")
def get_aggregator(customer_id: str):

    seed = sum(ord(c) for c in customer_id)
    random.seed(seed)

    linked_banks = random.randint(1, 4)
    monthly_inflow = random.randint(40000, 200000)
    emi_commitments = random.randint(0, 6)
    auto_debit_failures = random.randint(0, 3)

    # Derived Signals
    salary_stability = "Stable" if auto_debit_failures == 0 else "Declining"

    liquidity_ratio = monthly_inflow - (emi_commitments * 15000)

    if liquidity_ratio < 20000:
        liquidity_index = "High"
        liquidity_score = 0.8
    elif liquidity_ratio < 50000:
        liquidity_index = "Medium"
        liquidity_score = 0.5
    else:
        liquidity_index = "Low"
        liquidity_score = 0.2

    savings_trend = random.choice(["Positive", "Flat", "Negative"])
    spend_volatility = random.choice(["Low", "Medium", "High"])

    # 🔥 Composite Intelligence Layer
    base_behavior_risk = random.uniform(0.1, 0.9)

    composite_risk = base_behavior_risk

    if liquidity_index == "High":
        composite_risk += 0.1

    if salary_stability == "Declining":
        composite_risk += 0.05

    composite_risk = round(min(composite_risk, 1.0), 2)

    return {
        "linked_banks": linked_banks,
        "monthly_inflow": monthly_inflow,
        "emi_commitments": emi_commitments,
        "auto_debit_failures": auto_debit_failures,
        "salary_stability": salary_stability,
        "liquidity_index": liquidity_index,
        "savings_trend": savings_trend,
        "spend_volatility": spend_volatility,
        "composite_risk_score": composite_risk
    }


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    record = get_risk_record(customer_id)

    if not record:
        return {"error": "Customer not found"}

    return record


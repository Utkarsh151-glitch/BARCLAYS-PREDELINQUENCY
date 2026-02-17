from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import boto3
import random
from app.models import CustomerInput, CustomerRawInput
from app.risk_engine import calculate_risk
from app.predict_engine import predict_from_raw_input
from app.model_metrics_engine import get_model_metrics
from app.production_inference_engine import (
    get_customers_sample as get_customers_sample_inference,
    get_customer as get_customer_inference,
    get_customer_explanation as get_customer_explanation_inference,
)
from app.aws_clients import (
    save_risk_record,
    save_behavior_profile,
    send_alert
)
from app.config import AWS_REGION, DYNAMODB_RISK_TABLE



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
# Predict From Raw Customer Data
# -------------------------
@app.post("/predict")
def predict_customer_risk(customer: CustomerRawInput):
    try:
        probability, risk_level, top_features = predict_from_raw_input(customer)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return {
        "customer_id": customer.customer_id,
        "probability_score": round(probability, 4),
        "risk_level": risk_level,
        "top_3_contributing_features": top_features,
    }


# -------------------------
# Model Metrics
# -------------------------
@app.get("/model-metrics")
def model_metrics():
    try:
        return get_model_metrics()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to compute model metrics: {exc}")


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
def get_customers(
    limit: int = Query(200, ge=1, le=200),
    offset: int = Query(0, ge=0),
    mode: str = Query("top_risk"),
):
    try:
        return get_customers_sample_inference(limit=limit, offset=offset, mode=mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load customers sample: {exc}")


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


@app.get("/customers/{customer_id}/explain")
def get_customer_explain(customer_id: str):
    explanation = get_customer_explanation_inference(customer_id)
    if not explanation:
        raise HTTPException(status_code=404, detail="Customer not found")
    return explanation


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    customer = get_customer_inference(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


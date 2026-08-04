import sys
from pathlib import Path

# Ensure the project root is on sys.path so root-level modules
# (e.g. feature_engineering) can be imported when deployed on Render.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from datetime import datetime
import random

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.aws_clients import save_behavior_profile, save_risk_record, send_alert
from app.config import ALLOWED_ORIGINS
from app.model_metrics_engine import get_model_metrics
from app.models import CustomerInput, CustomerRawInput
from app.predict_engine import predict_from_raw_input
from app.production_inference_engine import (
    get_alerts as get_alerts_inference,
    get_customer as get_customer_inference,
    get_customer_explanation as get_customer_explanation_inference,
    get_customers_sample as get_customers_sample_inference,
    get_portfolio_summary as get_portfolio_summary_inference,
)
from app.risk_engine import calculate_risk


app = FastAPI(title="Pre-Delinquency Risk Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Pre-Delinquency Risk Engine is running"}


@app.post("/analyze")
def analyze_customer(customer: CustomerInput):
    input_data = customer.model_dump()
    result = calculate_risk(input_data)

    response = {
        "customer_id": customer.customer_id,
        **result,
        "timestamp": str(datetime.utcnow()),
    }

    save_risk_record(response)
    save_behavior_profile(customer.customer_id, input_data)

    if result["risk_level"] == "HIGH":
        send_alert(customer.customer_id, result["risk_score"])

    return response


@app.post("/predict")
def predict_customer_risk(customer: CustomerRawInput):
    try:
        probability, risk_level, top_features = predict_from_raw_input(customer)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc

    return {
        "customer_id": customer.customer_id,
        "probability_score": round(probability, 4),
        "risk_level": risk_level,
        "top_3_contributing_features": top_features,
    }


@app.get("/model-metrics")
def model_metrics():
    try:
        return get_model_metrics()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to compute model metrics: {exc}") from exc


@app.get("/portfolio-summary")
def portfolio_summary():
    return get_portfolio_summary_inference()


@app.get("/customers")
def get_customers(
    limit: int = Query(200, ge=1, le=200),
    offset: int = Query(0, ge=0),
    mode: str = Query("top_risk"),
):
    try:
        return get_customers_sample_inference(limit=limit, offset=offset, mode=mode)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to load customers sample: {exc}") from exc


@app.get("/alerts")
def get_alerts():
    return get_alerts_inference(limit=100)


@app.get("/aggregator/{customer_id}")
def get_aggregator(customer_id: str):
    seed = sum(ord(char) for char in customer_id)
    random.seed(seed)

    linked_banks = random.randint(1, 4)
    monthly_inflow = random.randint(40000, 200000)
    emi_commitments = random.randint(0, 6)
    auto_debit_failures = random.randint(0, 3)

    salary_stability = "Stable" if auto_debit_failures == 0 else "Declining"
    liquidity_ratio = monthly_inflow - (emi_commitments * 15000)

    if liquidity_ratio < 20000:
        liquidity_index = "High"
    elif liquidity_ratio < 50000:
        liquidity_index = "Medium"
    else:
        liquidity_index = "Low"

    savings_trend = random.choice(["Positive", "Flat", "Negative"])
    spend_volatility = random.choice(["Low", "Medium", "High"])

    composite_risk = random.uniform(0.1, 0.9)
    if liquidity_index == "High":
        composite_risk += 0.1
    if salary_stability == "Declining":
        composite_risk += 0.05

    return {
        "linked_banks": linked_banks,
        "monthly_inflow": monthly_inflow,
        "emi_commitments": emi_commitments,
        "auto_debit_failures": auto_debit_failures,
        "salary_stability": salary_stability,
        "liquidity_index": liquidity_index,
        "savings_trend": savings_trend,
        "spend_volatility": spend_volatility,
        "composite_risk_score": round(min(composite_risk, 1.0), 2),
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

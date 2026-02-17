# Pre-Delinquency Risk Intelligence Platform

Institutional-grade pre-delinquency monitoring platform that predicts customer repayment stress before default and provides portfolio, customer, and model intelligence dashboards.

## 1. What This Project Does

This project combines a machine learning risk engine with a React command center to:

- Predict pre-delinquency probability from 6-month behavioral banking data
- Classify customers into `HIGH`, `MEDIUM`, `LOW` risk buckets
- Surface portfolio-level risk trends and concentration
- Provide customer-level explainability and feature impact
- Support alerts and intervention workflows via AWS integrations

---

## 2. Current Build Snapshot

- Dashboard title: **Risk Intelligence Command Center**
- Total modeled customers: **100,000**
- Raw behavioral rows: **600,000** (6 months x 100,000 customers)
- Engineered feature rows: **100,000**
- Features used by model: **16**
- UI sample view: **200 customers** (for frontend performance)

Sample dashboard distribution (current):
- High Risk: `28.0%`
- Medium Risk: `7.5%`
- Low Risk: `64.5%`

---

## 3. Tech Stack

### Backend
- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- pandas, numpy
- scikit-learn, joblib
- boto3 (AWS DynamoDB + SNS)

### Frontend
- React 19
- Vite
- Tailwind CSS v4
- Recharts, ApexCharts
- Framer Motion
- React Router

### ML / Artifacts
- RandomForestClassifier model persisted at `ml/risk_model.pkl`
- Feature/training CSV artifacts in `data/`
- MLflow artifacts present under `ml/mlruns/`

---

## 4. Data and Feature Engineering

### Input contract for prediction
Exactly 6 months of per-customer time series:

- `monthly_salary`
- `emi_amount`
- `balance_daily_avg`
- `salary_credit_day`
- `auto_debit_failures`
- `discretionary_spend`
- `cash_withdrawals`

### Engineered features (16)
- `salary_mean`
- `salary_std`
- `salary_trend_slope`
- `salary_delay_avg`
- `salary_delay_max`
- `emi_to_income_ratio`
- `min_balance_last_3m`
- `balance_trend_slope`
- `balance_volatility`
- `auto_debit_failure_rate`
- `max_consecutive_failure_streak`
- `utility_payment_delay_avg`
- `bounce_proxy`
- `discretionary_spend_trend_slope`
- `discretionary_spend_volatility`
- `cash_withdrawal_spike_ratio`

---

## 5. Model Configuration

Model: `RandomForestClassifier`

- `n_estimators=500`
- `max_depth=10`
- `min_samples_leaf=20`
- `class_weight='balanced'`
- `random_state=42`
- Train/Test split: `80/20` stratified
- Synthetic target generation rate: `~30%` positive class

Risk level mapping (production inference):
- `HIGH` if score `> 0.7`
- `MEDIUM` if score `> 0.4`
- `LOW` otherwise

---

## 6. Current Model Metrics

- AUC: `0.9981`
- Precision: `0.9182`
- Recall: `0.9898`
- F1: `0.9526`
- Evaluated rows: `100000`

Top feature importance:
- `emi_to_income_ratio`
- `balance_trend_slope`
- `max_consecutive_failure_streak`
- `auto_debit_failure_rate`
- `salary_delay_max`

---

## 7. API Endpoints

Base URL: `http://127.0.0.1:8000`

- `GET /`  
  Service health message

- `POST /predict`  
  Predict risk from 6-month raw input

- `POST /analyze`  
  Legacy hybrid scoring flow with storage + alert hooks

- `GET /model-metrics`  
  Returns AUC/Precision/Recall/F1 and top feature importance

- `GET /portfolio-summary`  
  Portfolio risk counts

- `GET /customers?limit=200&offset=0&mode=top_risk|random`  
  Customer list for dashboard/table views

- `GET /customers/{customer_id}`  
  Single customer profile

- `GET /customers/{customer_id}/explain`  
  Top explanatory factors for customer risk

- `GET /alerts`  
  High-risk customer alerts feed

- `GET /aggregator/{customer_id}`  
  Synthetic account aggregation signals

---

## 8. Frontend Modules

- Dashboard
- Portfolio Risk
- Customers
- Customer Detail
- Alerts
- Model Intelligence

Key UI capabilities:
- KPI cards and risk distribution donut
- Feature importance visualization
- Sort/filter/search customer registry
- Customer risk profile and derived trend charts
- Threshold simulation (model intelligence page)

---

## 9. Project Structure

```text
BARCLAYS-PREDELINQUENCY/
├─ app/
│  ├─ main.py
│  ├─ models.py
│  ├─ production_inference_engine.py
│  ├─ predict_engine.py
│  ├─ model_metrics_engine.py
│  ├─ risk_engine.py
│  ├─ aws_clients.py
│  ├─ config.py
│  └─ ...
├─ data/
│  ├─ predelinquency_risk_dataset.csv
│  ├─ predelinquency_features.csv
│  └─ predelinquency_training_data.csv
├─ ml/
│  ├─ train_model.py
│  ├─ risk_model.pkl
│  └─ mlruns/
├─ frontend/
│  ├─ src/
│  ├─ package.json
│  └─ vite.config.js
├─ feature_engineering.py
└─ requirements.txt
10. Local Setup
Backend
bash

pip install -r requirements.txt
uvicorn app.main:app --reload
Frontend
bash

cd frontend
npm install
npm run dev
Frontend default: http://localhost:5173
Backend default: http://127.0.0.1:8000

11. AWS Configuration Used
In config.py:

AWS_REGION = "ap-south-1"
DYNAMODB_RISK_TABLE = "customer_risk_scores"
DYNAMODB_BEHAVIOR_TABLE = "customer_behavior_profiles"
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:...:predelinquency-alerts"
12. Notes
This repo contains both a newer production inference pipeline and a legacy hybrid engine path.
Some advanced modules (playbook/logging/time-series) are present for extension and can be wired further into production flows.

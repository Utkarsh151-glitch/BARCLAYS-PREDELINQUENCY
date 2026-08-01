# Pre-Delinquency Risk Intelligence Platform

Institutional-grade pre-delinquency monitoring platform that predicts customer repayment stress before default and provides portfolio, customer, alert, and model intelligence dashboards.

## What It Does

- Predicts pre-delinquency probability from six months of customer banking behavior.
- Classifies customers into `HIGH`, `MEDIUM`, and `LOW` risk buckets.
- Serves model metrics, portfolio summaries, customer lists, explanations, and alert feeds through FastAPI.
- Presents the risk command center through a React, Vite, Tailwind, Recharts, and Framer Motion frontend.

## Tech Stack

Backend:
- Python 3.11
- FastAPI, Uvicorn, Pydantic
- pandas, numpy, scikit-learn, joblib
- Optional AWS DynamoDB/SNS hooks through `AWS_ENABLED=true`

Frontend:
- React 19
- Vite
- Tailwind CSS v4
- Recharts, ApexCharts, Framer Motion, Lucide

ML:
- Production model: `ml/risk_model.pkl`
- Engineered features: `data/predelinquency_features.csv`
- Metrics data: `data/predelinquency_training_data.csv`

## API Endpoints

- `GET /`
- `POST /predict`
- `POST /analyze`
- `GET /model-metrics`
- `GET /portfolio-summary`
- `GET /customers?limit=200&offset=0&mode=top_risk|random`
- `GET /customers/{customer_id}`
- `GET /customers/{customer_id}/explain`
- `GET /alerts`
- `GET /aggregator/{customer_id}`

## Local Setup

Backend:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Local URLs:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`

## Render Backend Deploy

This repo includes `render.yaml`.

Use these settings if creating the service manually:
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Runtime: Python 3.11

Environment variables:

```text
AWS_ENABLED=false
ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
```

If AWS storage/alerts are required later, set:

```text
AWS_ENABLED=true
AWS_REGION=ap-south-1
DYNAMODB_RISK_TABLE=customer_risk_scores
DYNAMODB_BEHAVIOR_TABLE=customer_behavior_profiles
SNS_TOPIC_ARN=your-topic-arn
```

## Vercel Frontend Deploy

Set the Vercel project root to `frontend`.

Environment variable:

```text
VITE_API_BASE_URL=https://your-render-service.onrender.com
```

Build settings:
- Build command: `npm run build`
- Output directory: `dist`

## Deep Learning Layer

The current RandomForest model is the best deployment choice for this repo because it is already trained, explainable, fast, and small enough for Render. A true deep learning layer should be added only after training a sequence model on the raw six-month customer panel data, then comparing it against the current baseline with holdout AUC, recall, calibration, and latency.

Recommended next step:
- Add a separate experimental `ml/train_sequence_model.py` using a small temporal MLP/LSTM.
- Persist it as a separate artifact such as `ml/sequence_risk_model.*`.
- Add an ensemble endpoint only if the sequence model beats the RandomForest on validation data and stays within deployment memory limits.

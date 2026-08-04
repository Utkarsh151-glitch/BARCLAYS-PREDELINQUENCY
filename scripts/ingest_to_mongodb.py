import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
from pymongo import MongoClient, UpdateOne
import dns.resolver

# Workaround for local router DNS timeouts with MongoDB Atlas SRV records
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']

# Add root directory to sys.path to allow importing from app
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.config import MONGODB_URI, MONGODB_DB_NAME

MODEL_PATH = ROOT_DIR / "ml" / "risk_model.pkl"
FEATURES_PATH = ROOT_DIR / "data" / "predelinquency_features.csv"

def _normalize_customer_id(customer_id) -> str:
    if pd.isna(customer_id): return ""
    return str(int(customer_id)) if isinstance(customer_id, (float, np.floating)) and customer_id.is_integer() else str(customer_id)

def _risk_level(probability: float) -> str:
    if probability > 0.7: return "HIGH"
    if probability > 0.4: return "MEDIUM"
    return "LOW"

def _infer_model_features(model, columns) -> list[str]:
    if hasattr(model, "feature_names_in_"):
        return [str(x) for x in model.feature_names_in_]
    excluded = {"customer_id", "default_risk", "risk_score_raw", "timestamp", "risk_level", "risk_score"}
    return [col for col in columns if col not in excluded]

def _predict_probabilities(model, X: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        raw = model.decision_function(X)
        return 1.0 / (1.0 + np.exp(-raw))
    return model.predict(X).astype(float)

def ingest_data():
    uri = MONGODB_URI or input("Enter MongoDB Connection URI: ").strip().strip('"').strip("'")
    if not uri:
        print("Error: MONGODB_URI is required.")
        return

    print("Connecting to MongoDB...")
    client = MongoClient(uri)
    db = client[MONGODB_DB_NAME]
    collection = db["customers"]
    
    # Create indexes for fast querying
    collection.create_index("customer_id", unique=True)
    collection.create_index([("risk_score", -1)])
    collection.create_index("risk_level")

    print("Loading ML model...")
    model = joblib.load(MODEL_PATH)
    
    print("Processing features CSV in chunks...")
    chunk_size = 5000
    total_processed = 0
    
    for chunk in pd.read_csv(FEATURES_PATH, chunksize=chunk_size):
        model_features = _infer_model_features(model, chunk.columns)
        
        # Ensure all features exist
        for col in model_features:
            if col not in chunk.columns:
                chunk[col] = 0.0
                
        X = chunk[model_features].replace([np.inf, -np.inf], np.nan).fillna(0.0)
        probabilities = _predict_probabilities(model, X)
        
        chunk["risk_score"] = probabilities.astype(float)
        chunk["risk_level"] = chunk["risk_score"].apply(_risk_level)
        chunk["timestamp"] = datetime.utcnow().isoformat()
        
        # Prepare for MongoDB
        operations = []
        for _, row in chunk.iterrows():
            record = row.to_dict()
            record = {k: v.item() if isinstance(v, np.generic) else v for k, v in record.items() if pd.notna(v)}
            
            customer_id = _normalize_customer_id(record.get("customer_id"))
            if not customer_id:
                continue
            record["customer_id"] = customer_id
            
            # Upsert operation
            operations.append(
                UpdateOne(
                    {"customer_id": customer_id},
                    {"$set": record},
                    upsert=True
                )
            )
            
        if operations:
            collection.bulk_write(operations)
            total_processed += len(operations)
            print(f"Processed {total_processed} records...")

    print("Data ingestion complete!")

if __name__ == "__main__":
    ingest_data()

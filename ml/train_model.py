from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from feature_engineering import FEATURE_COLUMNS, build_training_dataset


RANDOM_STATE = 42
RAW_DATA_PATH = ROOT_DIR / "data" / "predelinquency_risk_dataset.csv"
FEATURE_DATA_PATH = ROOT_DIR / "data" / "predelinquency_features.csv"
TRAINING_DATA_PATH = ROOT_DIR / "data" / "predelinquency_training_data.csv"
MODEL_PATH = ROOT_DIR / "ml" / "risk_model.pkl"


def load_training_data() -> pd.DataFrame:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw dataset not found at {RAW_DATA_PATH}")

    raw_df = pd.read_csv(RAW_DATA_PATH)
    training_df = build_training_dataset(raw_df, seed=RANDOM_STATE, target_rate=0.30)

    # Persist artifacts for reproducibility and model metrics endpoint.
    FEATURE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    training_df[["customer_id"] + FEATURE_COLUMNS].to_csv(FEATURE_DATA_PATH, index=False)
    training_df.to_csv(TRAINING_DATA_PATH, index=False)
    return training_df


def train() -> None:
    df = load_training_data()

    X = df[FEATURE_COLUMNS].copy()
    y = df["default_risk"].astype(int).copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=500,
        max_depth=10,
        min_samples_leaf=20,
        random_state=RANDOM_STATE,
        class_weight="balanced",
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    preds = (proba >= 0.5).astype(int)

    accuracy = accuracy_score(y_test, preds)
    auc = roc_auc_score(y_test, proba)
    precision = precision_score(y_test, preds, zero_division=0)
    recall = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    cm = confusion_matrix(y_test, preds)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Train rows: {len(X_train)} | Test rows: {len(X_test)}")
    print(f"Class balance (risk=1): {y.mean():.3f}")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"AUC:       {auc:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1:        {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)
    print(f"Saved model to: {MODEL_PATH}")
    print(f"Saved engineered features to: {FEATURE_DATA_PATH}")
    print(f"Saved training data to: {TRAINING_DATA_PATH}")


if __name__ == "__main__":
    train()

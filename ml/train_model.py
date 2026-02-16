import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Set experiment
mlflow.set_experiment("PreDelinquencyRiskModel")

# Synthetic dataset (temporary demo)
np.random.seed(42)

data = pd.DataFrame({
    "salary_delay_days": np.random.normal(2, 2, 500),
    "savings_balance_drop_pct": np.random.normal(5, 3, 500),
    "utility_payment_delay_days": np.random.normal(1, 1, 500),
    "upi_lending_txn_count": np.random.randint(0, 5, 500),
    "discretionary_spend_drop_pct": np.random.normal(3, 2, 500),
    "atm_withdrawals_count": np.random.randint(0, 5, 500),
    "failed_autodebit": np.random.randint(0, 3, 500),
})

# Target variable
data["default_risk"] = (
    data["salary_delay_days"] +
    data["savings_balance_drop_pct"] +
    data["failed_autodebit"]
) > 8

X = data.drop("default_risk", axis=1)
y = data["default_risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

with mlflow.start_run():

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    # Log metrics
    mlflow.log_metric("accuracy", accuracy)

    # Log model PROPERLY
    mlflow.sklearn.log_model(model, "model")

    print("Model trained and logged with accuracy:", accuracy)

import pandas as pd
import numpy as np
from tsfresh import extract_features
from tsfresh.utilities.dataframe_functions import impute


def simulate_customer_history(input_data: dict, days: int = 30):
    """
    Simulate last N days behavioral time series
    based on current snapshot.
    """

    history = []

    for day in range(days):
        history.append({
            "customer_id": input_data["customer_id"],
            "day": day,
            "salary_delay_days": input_data["salary_delay_days"] + np.random.normal(0, 1),
            "savings_balance_drop_pct": input_data["savings_balance_drop_pct"] + np.random.normal(0, 2),
            "utility_payment_delay_days": input_data["utility_payment_delay_days"] + np.random.normal(0, 1),
            "upi_lending_txn_count": input_data["upi_lending_txn_count"] + np.random.normal(0, 1),
            "discretionary_spend_drop_pct": input_data["discretionary_spend_drop_pct"] + np.random.normal(0, 3),
            "atm_withdrawals_count": input_data["atm_withdrawals_count"] + np.random.normal(0, 1),
            "failed_autodebit": input_data["failed_autodebit"] + np.random.normal(0, 1),
        })

    df = pd.DataFrame(history)
    return df


def extract_behavior_features(time_series_df: pd.DataFrame):
    """
    Extract advanced behavioral features using tsfresh
    """

    extracted_features = extract_features(
        time_series_df,
        column_id="customer_id",
        column_sort="day"
    )

    impute(extracted_features)

    return extracted_features.iloc[0].to_dict()

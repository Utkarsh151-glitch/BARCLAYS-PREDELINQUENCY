import numpy as np
import pandas as pd

np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "salary_delay_days": np.random.poisson(2, n),
    "savings_balance_drop_pct": np.round(np.random.uniform(0, 0.5, n), 2),
    "utility_payment_delay_days": np.random.poisson(3, n),
    "upi_lending_txn_count": np.random.poisson(1.5, n),
    "discretionary_spend_drop_pct": np.round(np.random.uniform(0, 0.6, n), 2),
    "atm_withdrawals_count": np.random.poisson(2, n),
    "failed_autodebit": np.random.binomial(1, 0.15, n),
})

df["default_risk"] = (
    (df.salary_delay_days > 5).astype(int) +
    (df.savings_balance_drop_pct > 0.35).astype(int) +
    (df.failed_autodebit == 1).astype(int)
)

df["default_risk"] = (df["default_risk"] >= 2).astype(int)

df.to_csv("predelinquency_data.csv", index=False)
print("Dataset generated")

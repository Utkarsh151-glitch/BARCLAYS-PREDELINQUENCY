from pydantic import BaseModel


class CustomerInput(BaseModel):
    customer_id: str
    salary_delay_days: float
    savings_balance_drop_pct: float
    utility_payment_delay_days: float
    upi_lending_txn_count: float
    discretionary_spend_drop_pct: float
    atm_withdrawals_count: float
    failed_autodebit: float

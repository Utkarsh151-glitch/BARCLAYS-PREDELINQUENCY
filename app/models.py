from typing import List

from pydantic import BaseModel, model_validator


class CustomerInput(BaseModel):
    customer_id: str
    salary_delay_days: float
    savings_balance_drop_pct: float
    utility_payment_delay_days: float
    upi_lending_txn_count: float
    discretionary_spend_drop_pct: float
    atm_withdrawals_count: float
    failed_autodebit: float


class CustomerRawInput(BaseModel):
    customer_id: str
    monthly_salary: List[float]
    emi_amount: List[float]
    balance_daily_avg: List[float]
    salary_credit_day: List[int]
    auto_debit_failures: List[int]
    discretionary_spend: List[float]
    cash_withdrawals: List[float]

    @model_validator(mode="after")
    def validate_series_lengths(self):
        fields = [
            "monthly_salary",
            "emi_amount",
            "balance_daily_avg",
            "salary_credit_day",
            "auto_debit_failures",
            "discretionary_spend",
            "cash_withdrawals",
        ]
        lengths = {field: len(getattr(self, field, [])) for field in fields}

        distinct_lengths = set(lengths.values())
        if len(distinct_lengths) != 1:
            raise ValueError(f"All input series must have same length. Got lengths: {lengths}")

        months = distinct_lengths.pop()
        if months != 6:
            raise ValueError(f"Exactly 6 months of input are required. Got: {months}")

        return self

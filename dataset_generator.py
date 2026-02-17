import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def generate_dataset(
    num_customers: int = 100_000,
    num_months: int = 6,
    seed: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    # Base customer profile
    base_salary = np.clip(
        rng.lognormal(mean=np.log(55_000), sigma=0.45, size=num_customers),
        15_000,
        350_000,
    )
    emi_ratio = 0.08 + rng.beta(2.2, 5.5, size=num_customers) * 0.57
    base_emi = base_salary * emi_ratio
    base_credit_day = np.clip(np.round(rng.normal(3.5, 1.7, size=num_customers)), 1, 10)
    base_discretionary_ratio = rng.uniform(0.12, 0.42, size=num_customers)
    base_cash_ratio = rng.uniform(0.03, 0.14, size=num_customers)
    essential_ratio = rng.uniform(0.28, 0.52, size=num_customers)

    # Hidden stress process to make trajectories realistic
    stress_start = rng.beta(1.8, 7.0, size=num_customers)
    stress_slope = rng.normal(0.015, 0.03, size=num_customers)
    deteriorating_mask = rng.random(num_customers) < 0.35
    stress_slope[deteriorating_mask] += rng.uniform(0.03, 0.08, size=deteriorating_mask.sum())

    shock_mask = rng.random(num_customers) < 0.22
    shock_month = rng.integers(1, num_months + 1, size=num_customers)
    shock_impact = rng.uniform(0.08, 0.26, size=num_customers)

    # Storage arrays
    monthly_salary = np.zeros((num_customers, num_months))
    emi_amount = np.zeros((num_customers, num_months))
    balance_daily_avg = np.zeros((num_customers, num_months))
    salary_credit_day = np.zeros((num_customers, num_months), dtype=int)
    auto_debit_failures = np.zeros((num_customers, num_months), dtype=int)
    utility_payment_delay_days = np.zeros((num_customers, num_months))
    discretionary_spend = np.zeros((num_customers, num_months))
    cash_withdrawals = np.zeros((num_customers, num_months))

    prev_balance = base_salary * rng.uniform(0.35, 2.7, size=num_customers)

    for m in range(num_months):
        month_num = m + 1
        stress = stress_start + stress_slope * m + rng.normal(0.0, 0.025, size=num_customers)
        stress += shock_mask * (month_num >= shock_month) * shock_impact
        stress = np.clip(stress, 0.01, 0.98)

        salary_noise = rng.normal(0.0, 0.03, size=num_customers)
        month_salary = base_salary * (1.0 - 0.28 * stress + salary_noise)
        month_salary = np.clip(month_salary, 8_000, base_salary * 1.12)

        month_emi = np.clip(base_emi * (1.0 + rng.normal(0.0, 0.015, size=num_customers)), 2_000, None)

        credit_delay = rng.poisson(0.6 + 5.8 * stress, size=num_customers)
        month_credit_day = np.clip(base_credit_day + credit_delay, 1, 31).astype(int)

        month_discretionary = month_salary * base_discretionary_ratio * (1.0 - 0.48 * stress)
        month_discretionary *= 1.0 + rng.normal(0.0, 0.10, size=num_customers)
        month_discretionary = np.clip(month_discretionary, 500, month_salary * 0.60)

        month_cash = month_salary * base_cash_ratio * (1.0 + 1.25 * stress)
        month_cash *= 1.0 + rng.normal(0.0, 0.12, size=num_customers)
        month_cash = np.clip(month_cash, 0, month_salary * 0.35)

        essential_spend = month_salary * essential_ratio * (1.0 + rng.normal(0.0, 0.05, size=num_customers))
        essential_spend = np.clip(essential_spend, month_salary * 0.15, month_salary * 0.75)

        affordability = month_emi / np.maximum(month_salary, 1.0)
        low_balance_pressure = np.clip(-prev_balance / np.maximum(month_salary, 1.0), 0, 2.5)
        fail_lambda = (
            0.01
            + 0.14 * stress
            + 0.42 * np.clip(affordability - 0.42, 0, 1.2)
            + 0.12 * low_balance_pressure
        )
        fail_lambda = np.clip(fail_lambda, 0.001, 2.2)
        month_failures = np.clip(rng.poisson(fail_lambda), 0, 4)
        payment_delay = (
            rng.poisson(0.4 + 2.7 * stress, size=num_customers)
            + np.clip(month_failures - 1, 0, None)
            + (month_credit_day > 8).astype(int)
        )
        payment_delay = np.clip(payment_delay, 0, 20)

        unpaid_factor = np.where(month_failures > 0, 0.35, 0.0)
        emi_outflow = month_emi * (1.0 - unpaid_factor)
        penalty_fees = month_failures * rng.uniform(250, 650, size=num_customers)

        end_balance = (
            prev_balance
            + month_salary
            - emi_outflow
            - essential_spend
            - month_discretionary
            - month_cash
            - penalty_fees
            + rng.normal(0.0, 900, size=num_customers)
        )
        end_balance = np.clip(end_balance, -2.5 * base_salary, 5.5 * base_salary)
        month_balance_avg = (prev_balance + end_balance) / 2.0 + rng.normal(0.0, 350, size=num_customers)

        monthly_salary[:, m] = np.round(month_salary, 2)
        emi_amount[:, m] = np.round(month_emi, 2)
        balance_daily_avg[:, m] = np.round(month_balance_avg, 2)
        salary_credit_day[:, m] = month_credit_day
        auto_debit_failures[:, m] = month_failures
        utility_payment_delay_days[:, m] = payment_delay
        discretionary_spend[:, m] = np.round(month_discretionary, 2)
        cash_withdrawals[:, m] = np.round(month_cash, 2)

        prev_balance = end_balance

    customer_ids = np.repeat(np.arange(1, num_customers + 1), num_months)
    months = np.tile(np.arange(1, num_months + 1), num_customers)

    df = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "month": months,
            "monthly_salary": monthly_salary.reshape(-1, order="C"),
            "emi_amount": emi_amount.reshape(-1, order="C"),
            "balance_daily_avg": balance_daily_avg.reshape(-1, order="C"),
            "salary_credit_day": salary_credit_day.reshape(-1, order="C"),
            "auto_debit_failures": auto_debit_failures.reshape(-1, order="C"),
            "utility_payment_delay_days": utility_payment_delay_days.reshape(-1, order="C"),
            "discretionary_spend": discretionary_spend.reshape(-1, order="C"),
            "cash_withdrawals": cash_withdrawals.reshape(-1, order="C"),
        }
    )
    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic customer-month banking behavior data."
    )
    parser.add_argument("--customers", type=int, default=100_000, help="Number of unique customers.")
    parser.add_argument("--months", type=int, default=6, help="Number of months per customer.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--output",
        type=str,
        default="data/predelinquency_risk_dataset.csv",
        help="Output CSV path.",
    )
    args = parser.parse_args()

    df = generate_dataset(num_customers=args.customers, num_months=args.months, seed=args.seed)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Generated {args.customers} customers x {args.months} months = {len(df)} rows")
    print(f"Saved CSV to: {output_path}")


if __name__ == "__main__":
    main()

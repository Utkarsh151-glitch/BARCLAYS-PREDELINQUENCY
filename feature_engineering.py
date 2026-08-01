import argparse
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "customer_id",
    "month",
    "monthly_salary",
    "emi_amount",
    "balance_daily_avg",
    "salary_credit_day",
    "auto_debit_failures",
    "discretionary_spend",
    "cash_withdrawals",
]

FEATURE_COLUMNS = [
    "salary_mean",
    "salary_std",
    "salary_trend_slope",
    "salary_delay_avg",
    "salary_delay_max",
    "emi_to_income_ratio",
    "min_balance_last_3m",
    "balance_trend_slope",
    "balance_volatility",
    "auto_debit_failure_rate",
    "max_consecutive_failure_streak",
    "utility_payment_delay_avg",
    "bounce_proxy",
    "discretionary_spend_trend_slope",
    "discretionary_spend_volatility",
    "cash_withdrawal_spike_ratio",
]


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _trend_slope(df: pd.DataFrame, value_col: str) -> pd.Series:
    x_col = "__x"
    df_local = df.copy()
    df_local[x_col] = df_local["month"].astype(float)
    df_local["__xy"] = df_local[x_col] * df_local[value_col].astype(float)
    df_local["__x2"] = df_local[x_col] * df_local[x_col]

    grouped = df_local.groupby("customer_id", sort=False)
    count = grouped.size().astype(float)
    sum_x = grouped[x_col].sum()
    sum_y = grouped[value_col].sum()
    sum_xy = grouped["__xy"].sum()
    sum_x2 = grouped["__x2"].sum()

    denominator = (count * sum_x2 - sum_x * sum_x).replace(0, np.nan)
    slope = (count * sum_xy - sum_x * sum_y) / denominator
    return slope.fillna(0.0)


def _max_consecutive_streak(values: np.ndarray) -> int:
    max_streak = 0
    current = 0
    for value in values:
        if value > 0:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 0
    return int(max_streak)


def _prepare_raw(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values(["customer_id", "month"]).reset_index(drop=True)

    first_2m = df.groupby("customer_id", sort=False).head(2).groupby("customer_id", sort=False)
    baseline_credit = first_2m["salary_credit_day"].median()
    df["salary_delay_days"] = np.maximum(
        df["salary_credit_day"].astype(float) - df["customer_id"].map(baseline_credit).astype(float),
        0.0,
    )

    if "utility_payment_delay_days" not in df.columns:
        df["utility_payment_delay_days"] = (
            0.6 * df["salary_delay_days"] + 1.8 * df["auto_debit_failures"]
        ).clip(lower=0.0)

    return df


def engineer_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    _validate_columns(raw_df)
    df = _prepare_raw(raw_df)
    grouped = df.groupby("customer_id", sort=False)

    salary_mean = grouped["monthly_salary"].mean()
    salary_std = grouped["monthly_salary"].std(ddof=0).fillna(0.0)
    salary_trend_slope = _trend_slope(df, "monthly_salary")
    salary_delay_avg = grouped["salary_delay_days"].mean()
    salary_delay_max = grouped["salary_delay_days"].max()

    avg_emi = grouped["emi_amount"].mean()
    avg_salary = grouped["monthly_salary"].mean().replace(0, np.nan)
    emi_to_income_ratio = avg_emi / avg_salary

    min_balance_last_3m = grouped.tail(3).groupby("customer_id", sort=False)["balance_daily_avg"].min()
    balance_trend_slope = _trend_slope(df, "balance_daily_avg")
    balance_volatility = grouped["balance_daily_avg"].std(ddof=0).fillna(0.0)

    month_counts = grouped.size().astype(float)
    auto_debit_failure_rate = grouped["auto_debit_failures"].sum() / month_counts
    max_consecutive_failure_streak = grouped["auto_debit_failures"].apply(
        lambda series: _max_consecutive_streak(series.to_numpy())
    )

    utility_payment_delay_avg = grouped["utility_payment_delay_days"].mean()
    bounce_proxy = grouped["auto_debit_failures"].sum() + grouped["utility_payment_delay_days"].sum()

    discretionary_spend_trend_slope = _trend_slope(df, "discretionary_spend")
    discretionary_spend_volatility = grouped["discretionary_spend"].std(ddof=0).fillna(0.0)

    cash_max = grouped["cash_withdrawals"].max()
    cash_mean = grouped["cash_withdrawals"].mean().replace(0, np.nan)
    cash_withdrawal_spike_ratio = cash_max / cash_mean

    features = pd.concat(
        [
            salary_mean.rename("salary_mean"),
            salary_std.rename("salary_std"),
            salary_trend_slope.rename("salary_trend_slope"),
            salary_delay_avg.rename("salary_delay_avg"),
            salary_delay_max.rename("salary_delay_max"),
            emi_to_income_ratio.rename("emi_to_income_ratio"),
            min_balance_last_3m.rename("min_balance_last_3m"),
            balance_trend_slope.rename("balance_trend_slope"),
            balance_volatility.rename("balance_volatility"),
            auto_debit_failure_rate.rename("auto_debit_failure_rate"),
            max_consecutive_failure_streak.rename("max_consecutive_failure_streak"),
            utility_payment_delay_avg.rename("utility_payment_delay_avg"),
            bounce_proxy.rename("bounce_proxy"),
            discretionary_spend_trend_slope.rename("discretionary_spend_trend_slope"),
            discretionary_spend_volatility.rename("discretionary_spend_volatility"),
            cash_withdrawal_spike_ratio.rename("cash_withdrawal_spike_ratio"),
        ],
        axis=1,
    ).reset_index().rename(columns={"index": "customer_id"})

    features = features.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    for col in FEATURE_COLUMNS:
        features[col] = features[col].astype(float)
    features["max_consecutive_failure_streak"] = features["max_consecutive_failure_streak"].astype(int)

    return features.sort_values("customer_id").reset_index(drop=True)


def _zscore(series: pd.Series) -> pd.Series:
    std = float(series.std(ddof=0))
    if std < 1e-9:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - series.mean()) / std


def generate_probabilistic_target(
    features_df: pd.DataFrame,
    seed: int = 42,
    target_rate: float = 0.30,
) -> Tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    features = features_df

    high_emi = _zscore(features["emi_to_income_ratio"])
    declining_balance = _zscore(-features["balance_trend_slope"])
    increasing_salary_delay = _zscore(features["salary_delay_avg"] + 0.4 * features["salary_delay_max"])
    rising_failures = _zscore(
        features["auto_debit_failure_rate"] + 0.5 * features["max_consecutive_failure_streak"]
    )

    linear_risk = (
        1.25 * high_emi
        + 1.10 * declining_balance
        + 0.95 * increasing_salary_delay
        + 1.05 * rising_failures
    )
    risk_score_raw = 1.0 / (1.0 + np.exp(-linear_risk))

    random_noise = rng.normal(0.0, 0.08, size=len(features))
    combined = risk_score_raw + random_noise
    threshold = float(np.quantile(combined, 1.0 - target_rate))
    label = (combined > threshold).astype(int)

    return pd.Series(risk_score_raw, index=features.index), pd.Series(label, index=features.index)


def build_training_dataset(
    raw_df: pd.DataFrame,
    seed: int = 42,
    target_rate: float = 0.30,
) -> pd.DataFrame:
    features = engineer_features(raw_df)
    risk_score_raw, label = generate_probabilistic_target(
        features_df=features,
        seed=seed,
        target_rate=target_rate,
    )
    output = features.copy()
    output["risk_score_raw"] = risk_score_raw
    output["default_risk"] = label.astype(int)
    return output


def load_and_engineer(input_path: str) -> pd.DataFrame:
    raw_df = pd.read_csv(input_path)
    return engineer_features(raw_df)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Engineer banking-grade features from raw 6-month customer time series."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/predelinquency_risk_dataset.csv",
        help="Path to input raw panel CSV.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/predelinquency_features.csv",
        help="Path to output feature CSV.",
    )
    parser.add_argument(
        "--with-target",
        action="store_true",
        help="Also generate probabilistic target columns for training.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed used for target noise.")
    parser.add_argument(
        "--target-rate",
        type=float,
        default=0.30,
        help="Approximate positive class ratio for synthetic target.",
    )
    args = parser.parse_args()

    raw_df = pd.read_csv(args.input)
    if args.with_target:
        output_df = build_training_dataset(raw_df, seed=args.seed, target_rate=args.target_rate)
    else:
        output_df = engineer_features(raw_df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False)

    print(f"Input rows: {len(raw_df)}")
    print(f"Engineered customers: {output_df['customer_id'].nunique()}")
    if "default_risk" in output_df.columns:
        print(f"Risky class ratio: {output_df['default_risk'].mean():.3f}")
    print(f"Saved output to: {output_path}")


if __name__ == "__main__":
    main()

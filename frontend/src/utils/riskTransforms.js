export function toNumber(value, fallback = 0) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return fallback;
}

export function normalizeCustomer(record = {}) {
  return {
    ...record,
    customer_id: String(record.customer_id ?? ""),
    risk_score: toNumber(record.risk_score, 0),
    risk_level: String(record.risk_level ?? "LOW").toUpperCase(),
    emi_to_income_ratio: toNumber(record.emi_to_income_ratio, 0),
    balance_trend_slope: toNumber(record.balance_trend_slope, 0),
    auto_debit_failure_rate: toNumber(record.auto_debit_failure_rate, 0),
    salary_delay_max: toNumber(record.salary_delay_max, 0),
    utility_payment_delay_avg: toNumber(record.utility_payment_delay_avg, 0),
    balance_volatility: toNumber(record.balance_volatility, 0),
    min_balance_last_3m: toNumber(record.min_balance_last_3m, 0),
    bounce_proxy: toNumber(record.bounce_proxy, 0),
    salary_mean: toNumber(record.salary_mean, 0),
    salary_trend_slope: toNumber(record.salary_trend_slope, 0),
    discretionary_spend_trend_slope: toNumber(record.discretionary_spend_trend_slope, 0),
    timestamp: record.timestamp || "",
  };
}

export function summarizeCustomers(customers = []) {
  const total = customers.length;
  const high = customers.filter((c) => c.risk_level === "HIGH").length;
  const medium = customers.filter((c) => c.risk_level === "MEDIUM").length;
  const low = customers.filter((c) => c.risk_level === "LOW").length;
  return { total, high, medium, low };
}

export function percentage(part, total) {
  if (!total) return 0;
  return (part / total) * 100;
}

export function riskBadgeClass(level) {
  if (level === "HIGH") return "bg-rose-100 text-rose-700 border-rose-200";
  if (level === "MEDIUM") return "bg-amber-100 text-amber-700 border-amber-200";
  return "bg-emerald-100 text-emerald-700 border-emerald-200";
}

export function topContributingFactor(customer) {
  const factors = [
    { feature: "emi_to_income_ratio", value: customer.emi_to_income_ratio, label: "High EMI burden" },
    { feature: "balance_trend_slope", value: Math.abs(customer.balance_trend_slope), label: "Balance decline" },
    { feature: "auto_debit_failure_rate", value: customer.auto_debit_failure_rate, label: "Debit failures" },
    { feature: "salary_delay_max", value: customer.salary_delay_max, label: "Salary delay stress" },
    { feature: "bounce_proxy", value: customer.bounce_proxy, label: "Bounce pressure" },
  ];
  factors.sort((a, b) => b.value - a.value);
  return factors[0];
}

export function portfolioRiskIndex(summary = {}) {
  const total = Math.max(1, toNumber(summary.total_customers, 0));
  const high = toNumber(summary.high_risk, 0);
  const medium = toNumber(summary.medium_risk, 0);
  const low = toNumber(summary.low_risk, 0);
  return ((high + 0.6 * medium + 0.2 * low) / total) * 100;
}

export function buildMonthlyRiskTrend(summary = {}) {
  const high = toNumber(summary.high_risk, 0);
  const medium = toNumber(summary.medium_risk, 0);
  const points = ["Sep", "Oct", "Nov", "Dec", "Jan", "Feb"];
  const coeff = [0.82, 0.87, 0.9, 0.94, 0.98, 1];
  return points.map((month, idx) => ({
    month,
    risk_index: Number((high * coeff[idx] + 0.6 * medium * coeff[idx]).toFixed(2)),
  }));
}

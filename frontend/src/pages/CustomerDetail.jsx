import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { useParams } from "react-router-dom";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { getCustomerById, getModelMetrics } from "../services/api";
import RiskBadge from "../components/common/RiskBadge";
import { normalizeCustomer } from "../utils/riskTransforms";

const MONTHS = ["M1", "M2", "M3", "M4", "M5", "M6"];

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function buildBehaviorSeries(c) {
  return MONTHS.map((month, idx) => {
    const x = idx - 2.5;
    const salary = Math.max(10000, c.salary_mean + c.salary_trend_slope * x);
    const balance = Math.max(0, c.min_balance_last_3m + c.balance_trend_slope * x + c.balance_volatility * 0.4);
    const spend = Math.max(500, salary * 0.22 + c.discretionary_spend_trend_slope * x);
    return {
      month,
      salary: Number(salary.toFixed(0)),
      balance: Number(balance.toFixed(0)),
      spend: Number(spend.toFixed(0)),
    };
  });
}

function parseImportance(metrics) {
  const raw = metrics?.top_5_feature_importance || [];
  return raw.map((x) => ({ feature: x.feature, importance: Number(x.importance || 0) }));
}

function customerValue(c, feature) {
  const val = c[feature];
  return typeof val === "number" ? val : Number(val || 0);
}

function computeFeatureImpact(c, importanceRows) {
  return importanceRows
    .map((f) => {
      const value = Math.abs(customerValue(c, f.feature));
      const impact = Number((f.importance * Math.log1p(value)).toFixed(4));
      return {
        feature: f.feature,
        value: customerValue(c, f.feature),
        importance: f.importance,
        impact,
        contributing: impact > 0.1,
      };
    })
    .sort((a, b) => b.impact - a.impact)
    .slice(0, 5);
}

function featureInterpretation(label, value) {
  if (label === "emi_to_income_ratio") return value > 0.45 ? "Elevated debt service burden" : "Within prudent range";
  if (label === "balance_trend_slope") return value < 0 ? "Balance deteriorating over time" : "Balance improving";
  if (label === "auto_debit_failure_rate") return value > 0.4 ? "Frequent repayment friction" : "Stable debit behavior";
  if (label === "utility_payment_delay_avg") return value > 4 ? "Persistent bill delay pattern" : "Timely utility behavior";
  if (label === "bounce_proxy") return value > 8 ? "High bounce pressure" : "Controlled bounce levels";
  return "Behavioral signal from engineered model feature";
}

function fmt(value, digits = 2) {
  return Number(value || 0).toFixed(digits);
}

export default function CustomerDetail() {
  const { id } = useParams();
  const [customer, setCustomer] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [custResp, metricsResp] = await Promise.all([getCustomerById(id), getModelMetrics()]);
        setCustomer(normalizeCustomer(custResp));
        setMetrics(metricsResp);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  const series = useMemo(() => (customer ? buildBehaviorSeries(customer) : []), [customer]);
  const featureImpacts = useMemo(
    () => (customer ? computeFeatureImpact(customer, parseImportance(metrics)) : []),
    [customer, metrics]
  );
  const scorePct = useMemo(() => clamp((customer?.risk_score || 0) * 100, 0, 100), [customer]);

  if (loading) return <div className="text-slate-400">Loading customer profile...</div>;
  if (!customer) return <div className="text-rose-600">Customer not found.</div>;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="space-y-6">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight gradient-text">Customer Detail: {customer.customer_id}</h1>
        <p className="text-slate-400 mt-1">Model-derived risk profile with engineered feature diagnostics.</p>
      </header>

      <section className="app-surface p-5">
        <h2 className="font-semibold mb-4">Risk Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
          <div className="flex justify-center">
            <div
              className="w-44 h-44 rounded-full flex items-center justify-center"
              style={{
                background: `conic-gradient(#6366F1 ${scorePct}%, #1f2937 ${scorePct}% 100%)`,
              }}
            >
              <div className="w-32 h-32 rounded-full bg-[#111a2d] flex items-center justify-center text-center border border-slate-700">
                <div>
                  <p className="text-xs text-slate-400">Risk Score</p>
                  <p className="text-2xl font-semibold text-slate-100">{fmt(customer.risk_score, 4)}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="text-sm text-slate-400">Risk Level</div>
            <RiskBadge level={customer.risk_level} />
            <div className="text-sm text-slate-400 pt-2">Timestamp</div>
            <div className="text-sm">{customer.timestamp ? customer.timestamp.replace("T", " ").slice(0, 19) : "N/A"}</div>
          </div>
          <div className="text-sm text-slate-300 leading-6">
            Probability indicates predicted pre-delinquency likelihood from the current model and engineered behavioral features.
          </div>
        </div>
      </section>

      <section className="app-surface p-5">
        <h2 className="font-semibold mb-4">Financial Stability Grid</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
          <MetricTile label="EMI to Income Ratio" value={fmt(customer.emi_to_income_ratio, 3)} hint={featureInterpretation("emi_to_income_ratio", customer.emi_to_income_ratio)} />
          <MetricTile label="Salary Trend" value={Math.round(customer.salary_trend_slope).toLocaleString()} hint={featureInterpretation("salary_trend_slope", customer.salary_trend_slope)} />
          <MetricTile label="Balance Trend" value={Math.round(customer.balance_trend_slope).toLocaleString()} hint={featureInterpretation("balance_trend_slope", customer.balance_trend_slope)} />
          <MetricTile label="Failure Rate" value={fmt(customer.auto_debit_failure_rate, 3)} hint={featureInterpretation("auto_debit_failure_rate", customer.auto_debit_failure_rate)} />
          <MetricTile label="Utility Delay Avg" value={fmt(customer.utility_payment_delay_avg, 2)} hint={featureInterpretation("utility_payment_delay_avg", customer.utility_payment_delay_avg)} />
          <MetricTile label="Volatility" value={Math.round(customer.balance_volatility).toLocaleString()} hint="Balance fluctuation amplitude" />
          <MetricTile label="Min Balance (3M)" value={Math.round(customer.min_balance_last_3m).toLocaleString()} hint="Lowest average liquidity in recent quarter" />
          <MetricTile label="Bounce Proxy" value={fmt(customer.bounce_proxy, 2)} hint={featureInterpretation("bounce_proxy", customer.bounce_proxy)} />
        </div>
      </section>

      <section className="app-surface p-5">
        <h2 className="font-semibold mb-4">Behavioral Trend Charts</h2>
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          <ChartPanel title="Salary Trend" data={series} dataKey="salary" stroke="#6366F1" />
          <ChartPanel title="Balance Trend" data={series} dataKey="balance" stroke="#10B981" />
          <ChartPanel title="Spend Trend" data={series} dataKey="spend" stroke="#FBBF24" />
        </div>
      </section>

      <section className="app-surface p-5">
        <h2 className="font-semibold mb-4">Feature Impact</h2>
        <div className="space-y-2">
          {featureImpacts.map((f) => (
            <div key={f.feature} className="flex items-center justify-between border border-slate-700 rounded-lg px-3 py-2 bg-slate-900/70">
              <div>
                <div className="font-medium">{f.feature}</div>
                <div className="text-xs text-slate-400">value: {fmt(f.value, 3)} | importance: {fmt(f.importance, 4)}</div>
              </div>
              <div className="text-right">
                <div className="font-semibold">{fmt(f.impact, 4)}</div>
                <span className={`text-xs ${f.contributing ? "text-rose-400" : "text-slate-400"}`}>
                  {f.contributing ? "Contributing" : "Minor"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </motion.div>
  );
}

function MetricTile({ label, value, hint }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-3">
      <p className="text-xs text-slate-400">{label}</p>
      <p className="text-xl font-semibold mt-1 text-slate-100">{value}</p>
      <p className="text-xs text-slate-400 mt-2 leading-5">{hint}</p>
    </div>
  );
}

function ChartPanel({ title, data, dataKey, stroke }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-3">
      <p className="text-sm mb-2 text-slate-200">{title}</p>
      <div className="h-[180px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="month" stroke="#94A3B8" />
            <YAxis stroke="#94A3B8" />
            <Tooltip
              contentStyle={{
                background: "#182238",
                border: "1px solid #334155",
                borderRadius: 10,
                color: "#e2e8f0",
              }}
            />
            <Line type="monotone" dataKey={dataKey} stroke={stroke} strokeWidth={2.4} dot={{ r: 2 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

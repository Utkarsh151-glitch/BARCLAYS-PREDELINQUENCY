import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Activity, AlertTriangle, ShieldCheck, Users } from "lucide-react";
import { getCustomers, getModelMetrics } from "../services/api";
import KpiCard from "../components/common/KpiCard";
import FeatureImportanceChart from "../components/charts/FeatureImportanceChart";
import RiskBadge from "../components/common/RiskBadge";
import { normalizeCustomer, percentage, summarizeCustomers } from "../utils/riskTransforms";

const COLORS = ["#B94A48", "#5B6472", "#2F7D5C"];
const PERF_COLORS = {
  AUC: "bg-indigo-500",
  Precision: "bg-slate-700",
  Recall: "bg-emerald-500",
  F1: "bg-amber-400",
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [customerResp, metricsResp] = await Promise.all([
          getCustomers({ limit: 200, offset: 0, mode: "random" }),
          getModelMetrics(),
        ]);
        setCustomers((customerResp || []).map(normalizeCustomer));
        setMetrics(metricsResp);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const summary = useMemo(() => summarizeCustomers(customers), [customers]);
  const highRiskPct = percentage(summary.high, summary.total);
  const mediumRiskPct = percentage(summary.medium, summary.total);
  const lowRiskPct = percentage(summary.low, summary.total);

  const pieData = [
    { name: "High", value: summary.high },
    { name: "Medium", value: summary.medium },
    { name: "Low", value: summary.low },
  ];

  const balancedCustomers = useMemo(() => {
    const target = 10;
    const byLevel = {
      HIGH: [...customers].filter((c) => c.risk_level === "HIGH").sort((a, b) => b.risk_score - a.risk_score),
      MEDIUM: [...customers].filter((c) => c.risk_level === "MEDIUM").sort((a, b) => b.risk_score - a.risk_score),
      LOW: [...customers].filter((c) => c.risk_level === "LOW").sort((a, b) => b.risk_score - a.risk_score),
    };

    const ratio = {
      HIGH: Math.round((summary.high / Math.max(summary.total, 1)) * target),
      MEDIUM: Math.round((summary.medium / Math.max(summary.total, 1)) * target),
      LOW: Math.round((summary.low / Math.max(summary.total, 1)) * target),
    };

    const picked = [];
    const pull = (level, count) => {
      for (let i = 0; i < count && byLevel[level].length > 0; i += 1) picked.push(byLevel[level].shift());
    };

    pull("HIGH", ratio.HIGH);
    pull("MEDIUM", ratio.MEDIUM);
    pull("LOW", ratio.LOW);

    const fallbackOrder = ["HIGH", "MEDIUM", "LOW"];
    while (picked.length < target) {
      let added = false;
      for (const level of fallbackOrder) {
        if (byLevel[level].length > 0 && picked.length < target) {
          picked.push(byLevel[level].shift());
          added = true;
        }
      }
      if (!added) break;
    }

    return picked;
  }, [customers, summary.high, summary.low, summary.medium, summary.total]);

  if (loading) return <div className="text-slate-400">Loading dashboard intelligence...</div>;

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight gradient-text">Risk Intelligence Command Center</h1>
        <p className="text-slate-400 mt-1">Institutional pre-delinquency monitoring across active model outputs.</p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard title="Total Customers" value={summary.total} tone="indigo" subtext="Sampled for UI performance" />
        <KpiCard title="High Risk %" value={highRiskPct} suffix="%" tone="danger" subtext="Immediate intervention cohort" />
        <KpiCard title="Medium Risk %" value={mediumRiskPct} suffix="%" tone="warning" subtext="Watchlist and nudges" />
        <KpiCard title="Low Risk %" value={lowRiskPct} suffix="%" tone="success" subtext="Stable repayment behavior" />
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="app-surface accent-border p-4">
          <div className="flex items-center gap-2 mb-3">
            <Users size={16} className="text-indigo-400" />
            <h2 className="font-semibold">Risk Distribution</h2>
          </div>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" innerRadius={70} outerRadius={104} paddingAngle={1}>
                  {pieData.map((entry, idx) => (
                    <Cell key={entry.name} fill={COLORS[idx]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#FFFFFF",
                    border: "1px solid #E3E7ED",
                    borderRadius: 4,
                    color: "#1F2933",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs mt-2">
            <LegendPill color="bg-rose-500" label={`High: ${summary.high}`} />
            <LegendPill color="bg-amber-400" label={`Medium: ${summary.medium}`} />
            <LegendPill color="bg-emerald-500" label={`Low: ${summary.low}`} />
          </div>
        </div>

        <div className="app-surface accent-border p-4 xl:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck size={16} className="text-indigo-400" />
            <h2 className="font-semibold">Model Intelligence</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <div className="space-y-3">
              <PerfBar label="AUC" value={Number(metrics?.auc || 0)} />
              <PerfBar label="Precision" value={Number(metrics?.precision || 0)} />
              <PerfBar label="Recall" value={Number(metrics?.recall || 0)} />
              <PerfBar label="F1" value={Number(metrics?.f1 || 0)} />
            </div>
            <div>
              <FeatureImportanceChart data={metrics?.top_5_feature_importance || []} height={230} />
            </div>
          </div>
        </div>
      </section>

      <section className="app-surface accent-border p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle size={16} className="text-rose-400" />
            <h2 className="font-semibold">Recent Customers (Balanced Risk Mix)</h2>
          </div>
          <button
            onClick={() => navigate("/customers")}
            className="text-sm px-3 py-1.5 rounded border border-slate-700 hover:border-indigo-500 transition-colors"
            
          >
            View All
          </button>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-sm data-table min-w-[760px]">
            <thead className="border-b border-slate-700">
              <tr>
                <th className="py-3 text-left">Customer ID</th>
                <th className="py-3 text-left">Risk Score</th>
                <th className="py-3 text-left">Risk Level</th>
                <th className="py-3 text-left">EMI Ratio</th>
                <th className="py-3 text-left">Balance Trend</th>
              </tr>
            </thead>
            <tbody>
              {balancedCustomers.map((c) => (
                <tr
                  key={c.customer_id}
                  onClick={() => navigate(`/customers/${c.customer_id}`)}
                  className={`border-b border-slate-700 hover:bg-indigo-500/10 transition-colors cursor-pointer ${
                    c.risk_level === "HIGH"
                      ? "border-l-2 border-l-rose-500/60"
                      : c.risk_level === "MEDIUM"
                        ? "border-l-2 border-l-amber-400/60"
                        : "border-l-2 border-l-emerald-500/60"
                  }`}
                >
                  <td className="py-3 font-semibold num">{c.customer_id}</td>
                  <td className="py-3 num">{c.risk_score.toFixed(4)}</td>
                  <td className="py-3"><RiskBadge level={c.risk_level} /></td>
                  <td className="py-3 num">{c.emi_to_income_ratio.toFixed(3)}x</td>
                  <td className="py-3 num">{Math.round(c.balance_trend_slope).toLocaleString()} INR/mo</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <p className="text-xs text-slate-400">
        All KPI cards and Risk Distribution chart are computed from the same loaded customer sample ({summary.total} customers).
      </p>
    </div>
  );
}

function PerfBar({ label, value }) {
  const pct = Math.max(0, Math.min(100, value * 100));
  const barColor = PERF_COLORS[label] || "bg-indigo-500";
  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-1">
        <span className="text-slate-300 flex items-center gap-1"><Activity size={13} />{label}</span>
        <span className="text-slate-400">{value.toFixed(4)}</span>
      </div>
      <div className="h-2 rounded-full bg-slate-200">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.18 }}
          className={`h-2 rounded-full ${barColor}`}
        />
      </div>
    </div>
  );
}

function LegendPill({ color, label }) {
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-slate-700 px-2.5 py-1">
      <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
      <span className="text-slate-300">{label}</span>
    </div>
  );
}

import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { getModelMetrics, getPortfolioSummary } from "../services/api";
import FeatureImportanceChart from "../components/charts/FeatureImportanceChart";
import { buildMonthlyRiskTrend, portfolioRiskIndex } from "../utils/riskTransforms";

export default function PortfolioRisk() {
  const [summary, setSummary] = useState(null);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    async function loadData() {
      const [summaryResp, metricsResp] = await Promise.all([getPortfolioSummary(), getModelMetrics()]);
      setSummary(summaryResp);
      setMetrics(metricsResp);
    }
    loadData();
  }, []);

  const trend = useMemo(() => buildMonthlyRiskTrend(summary || {}), [summary]);
  const dist = useMemo(
    () =>
      summary
        ? [
            { name: "High", value: summary.high_risk, color: "#EF4444" },
            { name: "Medium", value: summary.medium_risk, color: "#F59E0B" },
            { name: "Low", value: summary.low_risk, color: "#10B981" },
          ]
        : [],
    [summary]
  );

  if (!summary) return <div className="text-slate-400">Loading portfolio risk analytics...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight gradient-text">Portfolio Risk Analytics</h1>
        <p className="text-slate-400 mt-2">
          Institutional view of segment concentration, trend drift, and model risk intelligence.
        </p>
      </div>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="panel-surface p-5">
          <p className="text-sm text-slate-400">Portfolio Risk Index</p>
          <p className="text-5xl font-semibold mt-3">{portfolioRiskIndex(summary).toFixed(1)}</p>
        </div>
        <div className="panel-surface p-5">
          <p className="text-sm text-slate-400">High Risk Exposure</p>
          <p className="text-5xl font-semibold mt-3">{Number(summary.high_risk || 0).toLocaleString()}</p>
        </div>
        <div className="panel-surface p-5">
          <p className="text-sm text-slate-400">AUC</p>
          <p className="text-5xl font-semibold mt-3">{Number(metrics?.auc || 0).toFixed(4)}</p>
        </div>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="panel-surface p-5">
          <h3 className="text-lg font-semibold mb-4">Risk Distribution</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={dist} dataKey="value" innerRadius={68} outerRadius={102}>
                  {dist.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#182238",
                    border: "1px solid #334155",
                    borderRadius: 10,
                    color: "#e2e8f0",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel-surface p-5 xl:col-span-2">
          <h3 className="text-lg font-semibold mb-4">Monthly Risk Index Trend</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
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
                <Area type="monotone" dataKey="risk_index" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.15} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="panel-surface p-5">
        <h3 className="text-lg font-semibold mb-4">Top Risk Drivers</h3>
        <FeatureImportanceChart data={metrics?.top_5_feature_importance || []} height={280} />
      </section>
    </div>
  );
}

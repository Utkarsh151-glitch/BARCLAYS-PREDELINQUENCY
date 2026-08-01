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
            { name: "High", value: summary.high_risk, color: "#B94A48" },
            { name: "Medium", value: summary.medium_risk, color: "#5B6472" },
            { name: "Low", value: summary.low_risk, color: "#2F7D5C" },
          ]
        : [],
    [summary]
  );

  if (!summary) return <div className="text-slate-400">Loading portfolio risk analytics...</div>;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight gradient-text">Portfolio Risk Analytics</h1>
        <p className="text-slate-400 mt-2">
          Institutional view of segment concentration, trend drift, and model risk intelligence.
        </p>
      </div>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="panel-surface p-4">
          <p className="text-sm text-slate-400">Portfolio Risk Index</p>
          <p className="text-3xl font-semibold mt-2 num">{portfolioRiskIndex(summary).toFixed(1)} pts</p>
        </div>
        <div className="panel-surface p-4">
          <p className="text-sm text-slate-400">High Risk Exposure</p>
          <p className="text-3xl font-semibold mt-2 num">{Number(summary.high_risk || 0).toLocaleString()} customers</p>
        </div>
        <div className="panel-surface p-4">
          <p className="text-sm text-slate-400">AUC</p>
          <p className="text-3xl font-semibold mt-2 num">{Number(metrics?.auc || 0).toFixed(4)}</p>
        </div>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        <div className="panel-surface p-4">
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
                    background: "#FFFFFF",
                    border: "1px solid #E3E7ED",
                    borderRadius: 4,
                    color: "#1F2933",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel-surface p-4 xl:col-span-2">
          <h3 className="text-lg font-semibold mb-4">Monthly Risk Index Trend</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E3E7ED" />
                <XAxis dataKey="month" stroke="#5B6472" />
                <YAxis stroke="#5B6472" />
                <Tooltip
                  contentStyle={{
                    background: "#FFFFFF",
                    border: "1px solid #E3E7ED",
                    borderRadius: 4,
                    color: "#1F2933",
                  }}
                />
                <Area type="monotone" dataKey="risk_index" stroke="#123C69" fill="#123C69" fillOpacity={0.08} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="panel-surface p-4">
        <h3 className="text-lg font-semibold mb-4">Top Risk Drivers</h3>
        <FeatureImportanceChart data={metrics?.top_5_feature_importance || []} height={280} />
      </section>
    </div>
  );
}

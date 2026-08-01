import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, SlidersHorizontal } from "lucide-react";
import { getCustomers } from "../services/api";
import RiskBadge from "../components/common/RiskBadge";
import { normalizeCustomer } from "../utils/riskTransforms";

export default function Customers() {
  const navigate = useNavigate();
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [minScore, setMinScore] = useState(0);
  const [sortDesc, setSortDesc] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await getCustomers({ limit: 200, offset: 0, mode: "random" });
        setRows((data || []).map(normalizeCustomer));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return [...rows]
      .filter((r) => (q ? r.customer_id.toLowerCase().includes(q) : true))
      .filter((r) => (riskFilter === "ALL" ? true : r.risk_level === riskFilter))
      .filter((r) => r.risk_score >= minScore)
      .sort((a, b) => (sortDesc ? b.risk_score - a.risk_score : a.risk_score - b.risk_score));
  }, [rows, search, riskFilter, minScore, sortDesc]);

  if (loading) return <div className="text-slate-400">Loading customers...</div>;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight gradient-text">Customer Risk Registry</h1>
        <p className="text-slate-400 mt-1">Sortable model-scored customer registry for analyst workflows.</p>
      </div>

      <section className="app-surface p-3">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-3">
          <div className="relative">
            <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search customer_id"
            className="w-full bg-slate-900/80 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:border-indigo-500"
            />
          </div>

          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-500"
          >
            <option value="ALL">All Risk Levels</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <div className="bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-1.5">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span>Minimum Risk Score</span>
              <span>{minScore.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>

          <button
            onClick={() => setSortDesc((s) => !s)}
            className="inline-flex items-center justify-center gap-2 bg-slate-900/80 border border-slate-700 rounded-lg px-3 py-2 text-sm hover:border-indigo-500 transition-colors"
          >
            <SlidersHorizontal size={15} />
            Sort Risk: {sortDesc ? "High to Low" : "Low to High"}
          </button>
        </div>
      </section>

      <section className="app-surface overflow-auto">
        <table className="w-full text-sm data-table min-w-[980px]">
          <thead className="border-b border-slate-700">
            <tr>
              <th className="px-4 py-3 text-left">Customer ID</th>
              <th className="px-4 py-3 text-left">Risk Score</th>
              <th className="px-4 py-3 text-left">Risk Level</th>
              <th className="px-4 py-3 text-left">EMI Ratio</th>
              <th className="px-4 py-3 text-left">Balance Trend</th>
              <th className="px-4 py-3 text-left">Failure Rate</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row, idx) => (
              <tr
                key={row.customer_id}
                onClick={() => navigate(`/customers/${row.customer_id}`)}
                className={`cursor-pointer border-b border-slate-700 hover:bg-indigo-500/10 transition-colors ${
                  row.risk_level === "HIGH"
                    ? "border-l-2 border-l-rose-500/70"
                    : row.risk_level === "MEDIUM"
                      ? "border-l-2 border-l-amber-400/70"
                      : "border-l-2 border-l-emerald-500/70"
                }`}
              >
                <td className="px-4 py-3 font-semibold num">{row.customer_id}</td>
                <td className="px-4 py-3">
                  <div className="w-40">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="num">{row.risk_score.toFixed(4)}</span>
                    </div>
                    <div className="h-2 rounded-full bg-slate-700">
                      <div
                        className={`h-2 rounded-full ${
                          row.risk_level === "HIGH"
                            ? "bg-rose-500"
                            : row.risk_level === "MEDIUM"
                              ? "bg-amber-400"
                              : "bg-emerald-500"
                        }`}
                        style={{ width: `${Math.min(100, row.risk_score * 100)}%` }}
                      />
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3"><RiskBadge level={row.risk_level} /></td>
                <td className="px-4 py-3 num">{row.emi_to_income_ratio.toFixed(3)}x</td>
                <td className="px-4 py-3 num">{Math.round(row.balance_trend_slope).toLocaleString()} INR/mo</td>
                <td className="px-4 py-3 num">{row.auto_debit_failure_rate.toFixed(3)}/mo</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

import { useEffect, useMemo, useState } from "react";
import { BellRing } from "lucide-react";
import { getCustomers } from "../services/api";
import RiskBadge from "../components/common/RiskBadge";
import { normalizeCustomer, topContributingFactor } from "../utils/riskTransforms";

export default function Alerts() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = (await getCustomers({ limit: 200, offset: 0, mode: "random" })) || [];
        const all = data.map(normalizeCustomer);
        const byLevel = {
          HIGH: all.filter((x) => x.risk_level === "HIGH").sort((a, b) => b.risk_score - a.risk_score),
          MEDIUM: all.filter((x) => x.risk_level === "MEDIUM").sort((a, b) => b.risk_score - a.risk_score),
          LOW: all.filter((x) => x.risk_level === "LOW").sort((a, b) => b.risk_score - a.risk_score),
        };

        const target = 24;
        const counts = {
          HIGH: Math.round(target * 0.45),
          MEDIUM: Math.round(target * 0.35),
          LOW: Math.round(target * 0.2),
        };

        const out = [];
        const pull = (level, n) => {
          for (let i = 0; i < n && byLevel[level].length > 0; i += 1) out.push(byLevel[level].shift());
        };
        pull("HIGH", counts.HIGH);
        pull("MEDIUM", counts.MEDIUM);
        pull("LOW", counts.LOW);

        while (out.length < target) {
          let added = false;
          for (const level of ["HIGH", "MEDIUM", "LOW"]) {
            if (byLevel[level].length > 0 && out.length < target) {
              out.push(byLevel[level].shift());
              added = true;
            }
          }
          if (!added) break;
        }

        setRows(out.sort((a, b) => b.risk_score - a.risk_score));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const ordered = useMemo(() => [...rows].sort((a, b) => b.risk_score - a.risk_score), [rows]);

  if (loading) return <div className="text-slate-500">Loading alerts...</div>;

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight gradient-text">Alerts Intelligence Feed</h1>
        <p className="text-slate-400 mt-1">Balanced risk feed across High, Medium, and Low cohorts.</p>
      </header>

      <div className="space-y-3">
        {ordered.map((row) => {
          const factor = topContributingFactor(row);
          return (
            <div
              key={row.customer_id}
              className={`app-surface border-l-4 p-3 panel-hover ${
                row.risk_level === "HIGH"
                  ? "border-l-rose-500"
                  : row.risk_level === "MEDIUM"
                    ? "border-l-amber-400"
                    : "border-l-emerald-500"
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div
                    className={`rounded-lg p-2 border ${
                      row.risk_level === "HIGH"
                        ? "bg-rose-100 border-rose-200"
                        : row.risk_level === "MEDIUM"
                          ? "bg-amber-100 border-amber-200"
                          : "bg-emerald-100 border-emerald-200"
                    }`}
                  >
                    <BellRing
                      size={16}
                      className={
                        row.risk_level === "HIGH"
                          ? "text-rose-400"
                          : row.risk_level === "MEDIUM"
                            ? "text-amber-300"
                            : "text-emerald-400"
                      }
                    />
                  </div>
                  <div>
                    <p className="font-semibold num">{row.customer_id}</p>
                    <p className="text-sm text-slate-500">
                      Top contributing factor: {factor.label} ({factor.feature})
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-semibold num">{row.risk_score.toFixed(4)}</span>
                  <RiskBadge level={row.risk_level} />
                  <span
                    className={`inline-flex rounded border px-2 py-1 text-xs ${
                      row.risk_level === "HIGH"
                        ? "border-rose-500/40 text-rose-300"
                        : row.risk_level === "MEDIUM"
                          ? "border-amber-400/40 text-amber-200"
                          : "border-emerald-500/40 text-emerald-300"
                    }`}
                  >
                    {row.risk_level === "HIGH" ? "Escalate" : row.risk_level === "MEDIUM" ? "Monitor" : "Cleared"}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

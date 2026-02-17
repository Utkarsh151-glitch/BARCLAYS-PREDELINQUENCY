import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from "recharts";

export default function FeatureImportanceChart({ data = [], height = 300 }) {
  const sorted = [...data].sort((a, b) => Number(b.importance || 0) - Number(a.importance || 0));
  const palette = ["#6366F1", "#06B6D4", "#10B981", "#FBBF24", "#F97316"];

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={sorted} layout="vertical" margin={{ left: 12, right: 24, top: 8, bottom: 8 }}>
          <XAxis type="number" stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <YAxis
            type="category"
            dataKey="feature"
            width={180}
            stroke="#64748b"
            tick={{ fill: "#cbd5e1", fontSize: 12 }}
          />
          <Tooltip
            cursor={{ fill: "rgba(59, 130, 246, 0.08)" }}
            contentStyle={{
              background: "#182238",
              border: "1px solid #334155",
              borderRadius: "10px",
              color: "#e2e8f0",
            }}
          />
          <Bar dataKey="importance" radius={[0, 8, 8, 0]} animationDuration={850}>
            {sorted.map((_, idx) => (
              <Cell key={idx} fill={palette[idx % palette.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

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
  const palette = ["#123C69", "#5B6472", "#2F7D5C", "#AAB2BD", "#E3E7ED"];

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={sorted} layout="vertical" margin={{ left: 12, right: 24, top: 8, bottom: 8 }}>
          <XAxis type="number" stroke="#AAB2BD" tick={{ fill: "#5B6472", fontSize: 12 }} />
          <YAxis
            type="category"
            dataKey="feature"
            width={180}
            stroke="#AAB2BD"
            tick={{ fill: "#3F4752", fontSize: 12 }}
          />
          <Tooltip
            cursor={{ fill: "rgba(18, 60, 105, 0.06)" }}
            contentStyle={{
              background: "#FFFFFF",
              border: "1px solid #E3E7ED",
              borderRadius: "4px",
              color: "#1F2933",
            }}
          />
          <Bar dataKey="importance" radius={[0, 2, 2, 0]} animationDuration={180}>
            {sorted.map((_, idx) => (
              <Cell key={idx} fill={palette[idx % palette.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

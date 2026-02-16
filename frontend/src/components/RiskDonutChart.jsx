import { PieChart, Pie, Cell, Tooltip } from "recharts";

export default function RiskDonutChart({ summary }) {

  const data = [
    { name: "High Risk", value: summary.high_risk },
    { name: "Medium Risk", value: summary.medium_risk },
    { name: "Low Risk", value: summary.low_risk },
  ];

  const COLORS = ["#f87171", "#fbbf24", "#34d399"];

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
      <h3 className="text-lg font-semibold mb-4">
        Risk Distribution
      </h3>

      <PieChart width={280} height={280}>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={70}
          outerRadius={100}
          paddingAngle={3}
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index]} />
          ))}
        </Pie>

        <Tooltip />
      </PieChart>
    </div>
  );
}

import { PieChart, Pie, Cell, Tooltip } from "recharts";

export default function RiskDonutChart({ summary }) {

  const data = [
    { name: "High Risk", value: summary.high_risk },
    { name: "Medium Risk", value: summary.medium_risk },
    { name: "Low Risk", value: summary.low_risk },
  ];

  const COLORS = ["#B94A48", "#5B6472", "#2F7D5C"];

  return (
    <div className="app-surface p-4">
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
          paddingAngle={1}
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

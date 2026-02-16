import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getPortfolioSummary } from "../services/api";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  LineChart,
  Line
} from "recharts";

export default function PortfolioRisk() {

  const [summary, setSummary] = useState(null);

  useEffect(() => {
    async function loadData() {
      const data = await getPortfolioSummary();
      setSummary(data);
    }
    loadData();
  }, []);

  if (!summary) {
    return <div className="text-slate-400">Loading analytics...</div>;
  }

  const pieData = [
    { name: "High", value: summary.high_risk },
    { name: "Medium", value: summary.medium_risk },
    { name: "Low", value: summary.low_risk },
  ];

  const trendData = [
    { month: "Jan", high: 3 },
    { month: "Feb", high: 4 },
    { month: "Mar", high: 5 },
    { month: "Apr", high: 6 },
    { month: "May", high: summary.high_risk },
  ];

  const COLORS = ["#f87171", "#fbbf24", "#34d399"];

  return (
    <div className="space-y-16">

      {/* HEADER */}
      <div>
        <h1 className="text-4xl font-semibold tracking-tight">
          Portfolio Risk Analytics
        </h1>
        <p className="text-slate-400 mt-2">
          Deep behavioral segmentation & exposure intelligence
        </p>
      </div>

      {/* GRID 1 */}
      <div className="grid grid-cols-2 gap-12">

        {/* DONUT */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 h-[420px]"
        >
          <h3 className="text-lg font-semibold mb-6">
            Risk Distribution
          </h3>

          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={pieData}
                innerRadius={90}
                outerRadius={130}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={index} fill={COLORS[index]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        {/* BAR */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 h-[420px]"
        >
          <h3 className="text-lg font-semibold mb-6">
            Segment Exposure
          </h3>

          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={pieData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip />
              <Bar
                dataKey="value"
                fill="#6366f1"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

      </div>

      {/* GRID 2 - TREND */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.7 }}
        className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 h-[420px]"
      >
        <h3 className="text-lg font-semibold mb-6">
          High Risk Trend Over Time
        </h3>

        <ResponsiveContainer width="100%" height="85%">
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="month" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="high"
              stroke="#f87171"
              strokeWidth={3}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

    </div>
  );
}

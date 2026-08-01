export default function RiskSummaryCard({ title, value, type }) {

  const colorMap = {
    high: "text-red-400",
    medium: "text-amber-400",
    low: "text-emerald-400",
    neutral: "text-indigo-400"
  };

  return (
    <div className="app-surface p-4 transition-colors duration-150">

      <p className="text-[11px] uppercase tracking-[0.06em] text-slate-400">
        {title}
      </p>

      <h2 className={`text-2xl font-semibold mt-2 num ${colorMap[type]}`}>
        {value}
      </h2>

    </div>
  );
}

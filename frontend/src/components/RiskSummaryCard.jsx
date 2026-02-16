export default function RiskSummaryCard({ title, value, type }) {

  const colorMap = {
    high: "text-red-400",
    medium: "text-amber-400",
    low: "text-emerald-400",
    neutral: "text-indigo-400"
  };

  return (
    <div className="p-8 rounded-2xl border 
      bg-slate-900/60 border-slate-800 
      hover:border-indigo-500/40 transition-all duration-300">

      <p className="text-xs uppercase tracking-widest text-slate-400">
        {title}
      </p>

      <h2 className={`text-4xl font-bold mt-4 ${colorMap[type]}`}>
        {value}
      </h2>

    </div>
  );
}

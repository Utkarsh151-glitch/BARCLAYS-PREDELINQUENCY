import AnimatedNumber from "./AnimatedNumber";

export default function KpiCard({ title, value, suffix = "", tone = "indigo", subtext = "" }) {
  const toneClass =
    tone === "danger"
      ? "border-l-rose-500"
      : tone === "warning"
        ? "border-l-slate-700"
        : tone === "success"
          ? "border-l-emerald-500"
          : "border-l-indigo-500";

  return (
    <div className={`app-surface panel-hover border-l-4 ${toneClass} p-4`}>
      <p className="text-[11px] uppercase tracking-[0.06em] text-slate-400">{title}</p>
      <p className="mt-2 text-2xl font-semibold num">
        <AnimatedNumber value={value} decimals={suffix === "%" ? 1 : 0} />
        {suffix}
      </p>
      <p className="mt-1 text-xs text-slate-400">{subtext}</p>
    </div>
  );
}

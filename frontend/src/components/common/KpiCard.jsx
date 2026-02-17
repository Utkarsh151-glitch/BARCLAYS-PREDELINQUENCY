import { motion } from "framer-motion";
import AnimatedNumber from "./AnimatedNumber";

export default function KpiCard({ title, value, suffix = "", tone = "indigo", subtext = "" }) {
  const toneClass =
    tone === "danger"
      ? "border-l-rose-500"
      : tone === "warning"
        ? "border-l-amber-400"
        : tone === "success"
          ? "border-l-emerald-500"
          : "border-l-indigo-500";

  const glowClass =
    tone === "danger"
      ? "shadow-rose-500/10"
      : tone === "warning"
        ? "shadow-amber-400/10"
        : tone === "success"
          ? "shadow-emerald-500/10"
          : "shadow-indigo-500/10";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`app-surface panel-hover border-l-4 ${toneClass} p-5 shadow-lg ${glowClass}`}
    >
      <p className="text-sm text-slate-400">{title}</p>
      <p className="mt-2 text-3xl font-semibold">
        <AnimatedNumber value={value} decimals={suffix === "%" ? 1 : 0} />
        {suffix}
      </p>
      <p className="mt-1 text-xs text-slate-400">{subtext}</p>
    </motion.div>
  );
}

import { riskBadgeClass } from "../../utils/riskTransforms";

export default function RiskBadge({ level }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold tracking-[0.04em] ${riskBadgeClass(level)}`}>
      {String(level || "LOW").toUpperCase()}
    </span>
  );
}

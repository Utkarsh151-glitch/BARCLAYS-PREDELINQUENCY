import { riskBadgeClass } from "../../utils/riskTransforms";

export default function RiskBadge({ level }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold tracking-wide ${riskBadgeClass(level)}`}>
      {String(level || "LOW").toUpperCase()}
    </span>
  );
}

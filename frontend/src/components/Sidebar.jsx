import { NavLink } from "react-router-dom";
import { Home, BarChart3, Users, AlertTriangle, BrainCircuit } from "lucide-react";

export const NAV_ITEMS = [
  { to: "/", icon: Home, label: "Dashboard" },
  { to: "/portfolio-risk", icon: BarChart3, label: "Portfolio Risk" },
  { to: "/customers", icon: Users, label: "Customers" },
  { to: "/alerts", icon: AlertTriangle, label: "Alerts" },
  { to: "/model-intelligence", icon: BrainCircuit, label: "Model Intelligence" },
];

// Desktop only: below lg the layout shows MobileNav instead, so the content gets the full width.
export default function Sidebar() {
  return (
    <aside className="hidden lg:flex w-72 shrink-0 bg-white border-r border-slate-700/80 p-6 flex-col justify-between">
      <div>
        <div className="mb-8 border-b border-slate-700 pb-5">
          <div className="inline-flex items-center gap-2 rounded-full border border-slate-700 bg-white px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-400">
            Risk Desk
          </div>
          <h1 className="text-xl font-semibold tracking-tight mt-3 leading-7">
            Pre-Delinquency
            <span className="block text-slate-400">Risk Intelligence</span>
          </h1>
        </div>

        <nav className="space-y-2.5">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <SidebarItem key={to} to={to} icon={<Icon size={18} />} label={label} />
          ))}
        </nav>
      </div>

      <div className="text-xs text-slate-500 border-t border-slate-700 pt-4 font-mono">
        Enterprise Risk Engine v2.0
      </div>
    </aside>
  );
}

function SidebarItem({ to, icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-150 border text-sm
        ${isActive
          ? "bg-white text-indigo-400 border-slate-700 border-l-4 border-l-indigo-500"
          : "text-slate-400 border-transparent hover:bg-slate-900/60 hover:border-slate-700"}`
      }
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </NavLink>
  );
}

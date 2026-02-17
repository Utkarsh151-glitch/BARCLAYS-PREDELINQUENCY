import { NavLink } from "react-router-dom";
import { Home, BarChart3, Users, AlertTriangle, BrainCircuit } from "lucide-react";

export default function Sidebar() {
  return (
    <aside className="w-72 shrink-0 bg-[#0f1a31]/90 border-r border-slate-700/80 p-7 flex flex-col justify-between backdrop-blur-md">
      <div>
        <div className="mb-10">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-400/30 bg-indigo-500/10 px-3 py-1 text-xs text-indigo-200">
            Innovation Lab
          </div>
          <h1 className="text-xl font-bold tracking-tight mt-3 leading-7">
            Pre-Delinquency
            <span className="block gradient-text">Risk Intelligence</span>
          </h1>
        </div>

        <nav className="space-y-2.5">
          <SidebarItem to="/" icon={<Home size={18} />} label="Dashboard" />
          <SidebarItem to="/portfolio-risk" icon={<BarChart3 size={18} />} label="Portfolio Risk" />
          <SidebarItem to="/customers" icon={<Users size={18} />} label="Customers" />
          <SidebarItem to="/alerts" icon={<AlertTriangle size={18} />} label="Alerts" />
          <SidebarItem to="/model-intelligence" icon={<BrainCircuit size={18} />} label="Model Intelligence" />
        </nav>
      </div>

      <div className="text-xs text-slate-500 border-t border-slate-700 pt-4">
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
        `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 border
        ${isActive
          ? "bg-gradient-to-r from-indigo-500/20 via-cyan-500/20 to-emerald-500/20 text-white border-indigo-400/50 shadow-[0_8px_18px_rgba(30,41,59,0.35)]"
          : "text-slate-300 border-transparent hover:bg-gradient-to-r hover:from-indigo-500/10 hover:to-cyan-500/10 hover:border-indigo-400/30 hover:text-white"}`
      }
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </NavLink>
  );
}

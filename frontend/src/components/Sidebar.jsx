import { NavLink } from "react-router-dom";
import { Home, BarChart3, Users, AlertTriangle, Database } from "lucide-react";



export default function Sidebar() {
  return (
    <div className="w-72 bg-[#0f172a] border-r border-slate-800 p-8 flex flex-col justify-between">

      <div>
        <h1 className="text-2xl font-semibold tracking-tight mb-12">
          Pre-Delinquency
          <span className="block text-indigo-400">AI</span>
        </h1>

        <nav className="space-y-4">

          <SidebarItem to="/" icon={<Home size={18} />} label="Dashboard" />
          <SidebarItem to="/portfolio-risk" icon={<BarChart3 size={18} />} label="Portfolio Risk" />
          <SidebarItem to="/customers" icon={<Users size={18} />} label="Customers" />
          <SidebarItem to="/alerts" icon={<AlertTriangle size={18} />} label="Alerts" />
          <SidebarItem to="/aggregator" icon={<Database size={18} />} label="Account Aggregator" />


         
        </nav>
      </div>

      <div className="text-xs text-slate-500">
        Risk Intelligence Engine v1.0
      </div>

    </div>
  );
}

function SidebarItem({ to, icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-3 rounded-xl transition-all
        ${isActive
          ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
          : "text-slate-400 hover:bg-slate-800 hover:text-white"}`
      }
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </NavLink>
  );
}

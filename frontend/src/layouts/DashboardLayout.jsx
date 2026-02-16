import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";

export default function DashboardLayout() {
  return (
    <div className="flex min-h-screen bg-[#0b1220] text-slate-100">

      {/* Subtle radial highlight */}
      <div className="fixed inset-0 pointer-events-none 
        bg-[radial-gradient(circle_at_20%_20%,rgba(99,102,241,0.12),transparent_40%)]" />

      <Sidebar />

      <main className="flex-1 relative px-12 py-10">
        <Outlet />
      </main>

    </div>
  );
}

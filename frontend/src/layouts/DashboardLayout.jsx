import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";

export default function DashboardLayout() {
  return (
    <div className="flex min-h-screen text-slate-100">
      <div className="fixed inset-0 pointer-events-none bg-[radial-gradient(circle_at_14%_8%,rgba(99,102,241,0.16),transparent_34%)]" />

      <Sidebar />

      <main className="flex-1 relative px-4 py-6 md:px-7 lg:px-10">
        <div className="max-w-7xl mx-auto w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import MobileNav from "../components/MobileNav";

export default function DashboardLayout() {
  return (
    <div className="flex flex-col lg:flex-row min-h-screen text-slate-100">
      <Sidebar />
      <MobileNav />

      <main className="flex-1 min-w-0 relative px-4 py-5 md:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

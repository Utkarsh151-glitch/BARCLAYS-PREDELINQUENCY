import { useEffect, useRef } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { NAV_ITEMS } from "./Sidebar";

// Compact header + horizontally scrollable tabs for phones and tablets (the sidebar takes over at lg).
export default function MobileNav() {
  const navRef = useRef(null);
  const { pathname } = useLocation();

  // Keep the active tab visible when the tab row is wider than the screen.
  useEffect(() => {
    const active = navRef.current?.querySelector('[aria-current="page"]');
    if (active) navRef.current.scrollTo({ left: active.offsetLeft - 16 });
  }, [pathname]);

  return (
    <header className="lg:hidden sticky top-0 z-30 bg-white border-b border-slate-700/80">
      <div className="px-4 pt-3 pb-2">
        <p className="text-[11px] font-semibold uppercase tracking-[0.08em] text-slate-400">Risk Desk</p>
        <p className="text-base font-semibold tracking-tight leading-6">Pre-Delinquency Risk Intelligence</p>
      </div>
      <nav ref={navRef} aria-label="Sections" className="flex gap-2 overflow-x-auto px-4 pb-3">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex shrink-0 items-center gap-2 px-3 py-2 rounded-xl border text-sm font-medium whitespace-nowrap
              ${isActive
                ? "bg-white text-indigo-400 border-slate-700 border-b-2 border-b-indigo-500"
                : "text-slate-400 border-transparent hover:bg-slate-900/60 hover:border-slate-700"}`
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}

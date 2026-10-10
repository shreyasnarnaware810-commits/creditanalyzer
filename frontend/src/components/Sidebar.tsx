import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  PlusCircle,
  FileSpreadsheet,
  History,
  Scale,
  Settings,
  Cpu
} from "lucide-react";

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: "/overview", label: "Overview Dashboard", icon: LayoutDashboard },
    { to: "/new-analysis", label: "New Credit Analysis", icon: PlusCircle },
    { to: "/applications", label: "Borrower Applications", icon: FileSpreadsheet },
    { to: "/decision-history", label: "Decision History & Audit", icon: History },
    { to: "/fairness-model", label: "Fairness & Model Panel", icon: Scale },
    { to: "/settings", label: "Settings & Disclaimers", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex-shrink-0 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between shadow-sm">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
          Platform Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-teal-50 text-teal-700 font-semibold shadow-xs border-l-4 border-teal-600"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </div>

      <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-1.5 text-xs text-slate-600">
        <div className="flex items-center gap-2 font-semibold text-slate-800">
          <Cpu className="w-4 h-4 text-teal-600" />
          <span>Model Registry</span>
        </div>
        <p className="text-[11px] leading-relaxed text-slate-500 font-mono">
          Model: <strong className="text-slate-700 font-sans">credence_gb_v1</strong><br />
          Target: <strong className="text-slate-700 font-sans">synthetic_default</strong>
        </p>
      </div>
    </aside>
  );
};

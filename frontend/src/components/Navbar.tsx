import React from "react";
import { useAuth } from "../context/AuthContext";
import { ShieldCheck, LogOut, UserCheck } from "lucide-react";

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-[#14243A] border-b border-[#1E3250] sticky top-0 z-40 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-[#0D9488] flex items-center justify-center shadow-sm">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-white">
                CREDENCE <span className="text-[#0D9488]">AI</span>
              </span>
              <span className="bg-teal-500/10 text-teal-300 text-[10px] font-semibold px-2 py-0.5 rounded border border-teal-500/20 uppercase tracking-wider">
                Production Prototype
              </span>
            </div>
            <p className="text-[11px] text-slate-300/80 hidden sm:block">
              Explainable Alternative Credit Scoring & Informal Income Synthesizer
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-[#1E3250] border border-[#2A4365]">
                <UserCheck className="w-4 h-4 text-[#0D9488]" />
                <div className="text-left">
                  <div className="text-xs font-semibold text-white leading-tight">{user.full_name}</div>
                  <div className="text-[10px] text-slate-300 capitalize flex items-center gap-1">
                    <span className={`w-1.5 h-1.5 rounded-full ${user.role === "officer" ? "bg-teal-400" : "bg-blue-400"}`}></span>
                    {user.role} Account
                  </div>
                </div>
              </div>

              <button
                onClick={logout}
                title="Sign out"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors border border-transparent"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

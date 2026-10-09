import React from "react";
import { useAuth } from "../context/AuthContext";
import { Settings, AlertCircle, Server } from "lucide-react";

export const SettingsPage: React.FC = () => {
  const { user, logout } = useAuth();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm">
        <h1 className="text-xl font-extrabold text-[#14243A] flex items-center gap-2">
          <Settings className="w-5 h-5 text-[#0D9488]" /> Settings & Prototype Specifications
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          System metadata, active session details, ML model registry, and transparent prototype disclosures.
        </p>
      </div>

      {/* Account Info */}
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900">Active Session Details</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1">
            <span className="text-slate-500 font-medium">Full Name</span>
            <div className="font-bold text-slate-900">{user?.full_name}</div>
          </div>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1">
            <span className="text-slate-500 font-medium">Username</span>
            <div className="font-bold text-slate-900">{user?.username}</div>
          </div>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1">
            <span className="text-slate-500 font-medium">Assigned Role</span>
            <div className="font-bold text-[#0D9488] uppercase">{user?.role}</div>
          </div>
          <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-1">
            <span className="text-slate-500 font-medium">Session Status</span>
            <div className="font-bold text-emerald-700">Authenticated</div>
          </div>
        </div>

        <button
          onClick={logout}
          className="px-4 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-bold text-xs rounded-lg transition-all"
        >
          Sign Out
        </button>
      </div>

      {/* Model & Architecture Specifications */}
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Server className="w-4 h-4 text-[#0D9488]" /> Active Model & Pipeline Specifications
        </h2>

        <div className="space-y-3 text-xs text-slate-700">
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex justify-between">
            <span className="text-slate-500 font-medium">Model Version:</span>
            <span className="font-mono font-bold text-[#0D9488]">credence_gb_v1</span>
          </div>
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex justify-between">
            <span className="text-slate-500 font-medium">Classifier Algorithm:</span>
            <span className="font-mono text-slate-900">GradientBoostingClassifier (n_est=150, depth=3)</span>
          </div>
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex justify-between">
            <span className="text-slate-500 font-medium">SHAP Explainer:</span>
            <span className="font-mono text-slate-900">shap.TreeExplainer (Log-Odds Additivity Verified)</span>
          </div>
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 flex justify-between">
            <span className="text-slate-500 font-medium">Scorecard Transformation:</span>
            <span className="font-mono text-slate-900">Base=600, Good/Bad Odds=20, PDO=40</span>
          </div>
        </div>
      </div>

      {/* Prototype Limitations Disclosure */}
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-600" /> Prototype Limitations & Production Path
        </h2>

        <ul className="list-disc list-inside text-xs text-slate-600 space-y-2 leading-relaxed">
          <li>The model is trained on synthetic data, not real-world loan repayment outcomes.</li>
          <li>Default probabilities are not calibrated to a real lending population.</li>
          <li>Score thresholds and loan policy multipliers are illustrative choices for demonstration.</li>
          <li>Fraud checks are transparent heuristics designed to alert human loan officers, not automatic rejection triggers.</li>
          <li>Real lending deployment requires formal legal, privacy, compliance, model-risk, and production identity governance.</li>
        </ul>
      </div>
    </div>
  );
};

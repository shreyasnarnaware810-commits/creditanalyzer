import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { History } from "lucide-react";

export const DecisionHistoryPage: React.FC = () => {
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getApplications()
      .then((data) => setApplications(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm">
        <h1 className="text-xl font-extrabold text-[#14243A] flex items-center gap-2">
          <History className="w-5 h-5 text-[#0D9488]" /> Decision History & Traceability Audit Log
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Complete audit history mapping score calculations, SHAP explanations, policy recommendations, and officer override rationale.
        </p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
        {loading ? (
          <div className="text-center py-12 text-xs text-slate-400">Loading decision history...</div>
        ) : applications.length === 0 ? (
          <div className="text-center py-12 text-xs text-slate-400 font-medium">No recorded decisions in system.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                  <th className="py-3 px-4">Application ID</th>
                  <th className="py-3 px-4">Borrower Name</th>
                  <th className="py-3 px-4">Requested Amount</th>
                  <th className="py-3 px-4">Latest Score</th>
                  <th className="py-3 px-4">Decision Status</th>
                  <th className="py-3 px-4">Assigned Officer</th>
                  <th className="py-3 px-4">Last Updated</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {applications.map((app) => (
                  <tr key={app.id} className="hover:bg-slate-50/80">
                    <td className="py-3.5 px-4 font-mono font-semibold text-[#0D9488]">{app.id}</td>
                    <td className="py-3.5 px-4 font-bold text-slate-900">{app.borrower_name}</td>
                    <td className="py-3.5 px-4 text-slate-700 font-medium">₹{app.requested_amount?.toLocaleString()}</td>
                    <td className="py-3.5 px-4 font-bold text-slate-900">{app.score || "-"}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-0.5 rounded-full border text-[11px] font-semibold bg-slate-100 text-slate-800 border-slate-200">
                        {app.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">{app.assigned_officer_id || "System Underwriting"}</td>
                    <td className="py-3.5 px-4 text-slate-500">{new Date(app.updated_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

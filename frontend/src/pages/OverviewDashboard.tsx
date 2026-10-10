import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import {
  PlusCircle,
  Users,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  ShieldCheck,
  Search,
  FileSpreadsheet
} from "lucide-react";

export const OverviewDashboard: React.FC = () => {
  const { user } = useAuth();
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const loadData = async () => {
    try {
      const data = await api.getApplications();
      setApplications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalApps = applications.length;
  const approvedApps = applications.filter((a) => a.status === "Approved").length;
  const pendingApps = applications.filter((a) => a.status === "Under Review" || a.status === "Submitted").length;
  const avgScore = totalApps > 0
    ? Math.round(applications.reduce((acc, a) => acc + (a.score || 600), 0) / totalApps)
    : 600;

  const filteredApps = applications.filter(
    (a) =>
      (a.borrower_name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-2xl shadow-sm">
        <div>
          <h1 className="text-xl font-extrabold text-[#14243A] flex items-center gap-2">
            Welcome back, {user?.full_name}
            <span className="text-xs bg-teal-50 text-[#0D9488] border border-teal-200 px-2.5 py-0.5 rounded-full capitalize font-semibold">
              {user?.role} Portal
            </span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time executive dashboard summarizing active credit applications, data quality ratings, and risk scores.
          </p>
        </div>

        <div>
          <Link
            to="/new-analysis"
            className="px-4 py-2.5 rounded-lg bg-[#0D9488] hover:bg-[#0F766E] text-xs font-bold text-white shadow-sm flex items-center gap-2 transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            New Credit Analysis
          </Link>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-medium text-slate-500">
            <span>Total Applications</span>
            <Users className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-black text-slate-900">{totalApps}</div>
          <div className="text-[11px] text-slate-400">Active records in system</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-medium text-slate-500">
            <span>Approved Applications</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-emerald-600">{approvedApps}</div>
          <div className="text-[11px] text-slate-400">Approved by underwriting</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-medium text-slate-500">
            <span>Pending Review</span>
            <Clock className="w-4 h-4 text-amber-600" />
          </div>
          <div className="text-2xl font-black text-amber-600">{pendingApps}</div>
          <div className="text-[11px] text-slate-400">Awaiting officer review</div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-xs font-medium text-slate-500">
            <span>Mean Credit Score</span>
            <ShieldCheck className="w-4 h-4 text-teal-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{avgScore}</div>
          <div className="text-[11px] text-slate-400">Scale 300 – 900</div>
        </div>
      </div>

      {/* Applications Table */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Application Queue</h2>
            <p className="text-xs text-slate-500">Select an application record to inspect data quality, score, SHAP explanation, and decision log.</p>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search applicant or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#0D9488] focus:bg-white w-full sm:w-64 transition-colors"
            />
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-xs text-slate-400">Loading applications from database...</div>
        ) : filteredApps.length === 0 ? (
          <div className="text-center py-12 border-2 border-dashed border-slate-200 rounded-xl space-y-3">
            <FileSpreadsheet className="w-10 h-10 text-slate-300 mx-auto" />
            <div className="text-sm font-bold text-slate-700">No Application Records Found</div>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Start by uploading transaction CSV records to create a new application analysis.
            </p>
            <Link
              to="/new-analysis"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-[#0D9488] hover:bg-[#0F766E] text-xs font-bold text-white shadow-xs transition-all mt-2"
            >
              <PlusCircle className="w-3.5 h-3.5" /> Create New Analysis
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50/50">
                  <th className="py-3 px-4">Application ID</th>
                  <th className="py-3 px-4">Borrower Name</th>
                  <th className="py-3 px-4">Requested Loan</th>
                  <th className="py-3 px-4">Est. Score</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created Date</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredApps.map((app) => {
                  let statusBadge = "bg-amber-50 text-amber-800 border-amber-200";
                  if (app.status === "Approved") statusBadge = "bg-emerald-50 text-emerald-800 border-emerald-200";
                  if (app.status === "Declined") statusBadge = "bg-rose-50 text-rose-800 border-rose-200";

                  return (
                    <tr key={app.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3.5 px-4 font-mono font-semibold text-[#0D9488]">{app.id}</td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">{app.borrower_name}</td>
                      <td className="py-3.5 px-4 font-medium text-slate-700">₹{app.requested_amount?.toLocaleString()}</td>
                      <td className="py-3.5 px-4">
                        {app.score ? (
                          <span className="font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                            {app.score}
                          </span>
                        ) : (
                          <span className="text-slate-400 italic">Pending analysis</span>
                        )}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-1 rounded-full border text-[11px] font-semibold ${statusBadge}`}>
                          {app.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-500">{new Date(app.created_at).toLocaleDateString()}</td>
                      <td className="py-3.5 px-4 text-right">
                        <Link
                          to={`/applications/${app.id}`}
                          className="inline-flex items-center gap-1 text-[#0D9488] hover:text-[#0F766E] font-bold text-xs"
                        >
                          View Analysis <ArrowUpRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

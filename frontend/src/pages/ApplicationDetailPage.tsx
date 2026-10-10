import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { ScoreGauge } from "../components/ScoreGauge";
import { DataQualityBadge } from "../components/DataQualityBadge";
import { ShapWaterfallChart } from "../components/ShapWaterfallChart";
import {
  FileText,
  BarChart3,
  HelpCircle,
  Sliders,
  CheckSquare,
  History,
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  XCircle,
  Info,
  Lock,
  Download
} from "lucide-react";

export const ApplicationDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [app, setApp] = useState<any>(null);
  const [analysisRun, setAnalysisRun] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<"summary" | "result" | "explain" | "whatif" | "decision" | "audit">("summary");
  const [loading, setLoading] = useState(true);

  // What-if simulator state
  const [whatifStable, setWhatifStable] = useState<number>(0);
  const [whatifPunc, setWhatifPunc] = useState<number>(0.85);
  const [whatifBuffer, setWhatifBuffer] = useState<number>(1.0);
  const [whatifAmount, setWhatifAmount] = useState<number>(60000);
  const [whatifResult, setWhatifResult] = useState<any>(null);
  const [whatifSimulating, setWhatifSimulating] = useState(false);

  // Officer decision form state
  const [decisionStatus, setDecisionStatus] = useState<string>("Approved");
  const [approvedAmount, setApprovedAmount] = useState<number>(50000);
  const [overrideReason, setOverrideReason] = useState<string>("");
  const [decisionNotes, setDecisionNotes] = useState<string>("");
  const [decisionSubmitting, setDecisionSubmitting] = useState(false);
  const [decisionError, setDecisionError] = useState<string | null>(null);
  const [decisionSuccess, setDecisionSuccess] = useState<string | null>(null);
  const [downloadingReport, setDownloadingReport] = useState(false);

  const loadAllData = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const appData = await api.getApplication(id);
      setApp(appData);

      if (appData.latest_analysis_run_id) {
        const arData = await api.getAnalysisRun(appData.latest_analysis_run_id);
        setAnalysisRun(arData);
        
        setWhatifStable(arData.cashflow.stable_monthly_cash_flow);
        setWhatifPunc(0.85);
        setWhatifBuffer(1.0);
        setWhatifAmount(arData.loan_policy.requested_amount);
        setApprovedAmount(arData.loan_policy.recommended_amount);
      }

      const logs = await api.getAuditHistory(id);
      setAuditLogs(logs);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, [id]);

  const handleDownloadReport = async () => {
    if (!app?.latest_analysis_run_id) return;
    setDownloadingReport(true);
    try {
      await api.downloadReport(app.latest_analysis_run_id, `Credence_AI_Assessment_${app.id}.pdf`);
    } catch (err: any) {
      console.error(err);
      alert("Failed to download PDF assessment report.");
    } finally {
      setDownloadingReport(false);
    }
  };

  const handleRunWhatIf = async () => {
    if (!analysisRun) return;
    setWhatifSimulating(true);
    try {
      const res = await api.runWhatIf({
        analysis_run_id: analysisRun.analysis_run_id,
        stable_cash_flow: whatifStable,
        utility_punctuality: whatifPunc,
        month_end_buffer: whatifBuffer,
        requested_amount: whatifAmount
      });
      setWhatifResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setWhatifSimulating(false);
    }
  };

  const handleRecordDecision = async (e: React.FormEvent) => {
    e.preventDefault();
    setDecisionError(null);
    setDecisionSuccess(null);

    if (user?.role !== "officer") {
      setDecisionError("Only Loan Officers can record underwriting decisions.");
      return;
    }

    setDecisionSubmitting(true);
    try {
      const res = await api.recordDecision(id!, {
        status: decisionStatus,
        approved_amount: approvedAmount,
        override_reason: overrideReason,
        notes: decisionNotes
      });
      setDecisionSuccess(res.message);
      await loadAllData();
    } catch (err: any) {
      setDecisionError(err.message || "Failed to record decision");
    } finally {
      setDecisionSubmitting(false);
    }
  };

  if (loading) {
    return <div className="text-center py-20 text-xs text-slate-500 font-medium">Loading application analysis...</div>;
  }

  if (!app) {
    return (
      <div className="text-center py-20 space-y-4">
        <div className="text-base font-bold text-slate-800">Application Record Not Found</div>
        <Link to="/overview" className="text-xs text-[#0D9488] font-bold underline">Back to Overview</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <Link to="/overview" className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-900 font-medium mb-2">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Queue
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-extrabold text-slate-900">{app.borrower_name}</h1>
            <span className="font-mono text-xs bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded font-semibold border border-slate-200">
              {app.id}
            </span>
          </div>
          <div className="text-xs text-slate-500 mt-1 flex items-center gap-4">
            <span>Requested Amount: <strong className="text-slate-900">₹{app.requested_amount?.toLocaleString()}</strong></span>
            <span>Status: <strong className="text-amber-700 font-bold">{app.status}</strong></span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {app.latest_analysis_run_id && (
            <button
              onClick={handleDownloadReport}
              disabled={downloadingReport}
              className="px-3.5 py-2 rounded-lg bg-[#0D9488] hover:bg-[#0F766E] text-white text-xs font-bold shadow-xs flex items-center gap-1.5 transition-all disabled:opacity-50 cursor-pointer"
            >
              <Download className="w-3.5 h-3.5" />
              <span>{downloadingReport ? "Generating PDF..." : "Download Assessment Report"}</span>
            </button>
          )}

          {analysisRun && (
            <DataQualityBadge
              level={analysisRun.data.data_confidence}
              warnings={analysisRun.data.warnings}
            />
          )}
        </div>
      </div>


      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200 space-x-2 overflow-x-auto bg-white px-4 pt-2 rounded-t-xl border">
        <button
          onClick={() => setActiveTab("summary")}
          className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all shrink-0 ${
            activeTab === "summary" ? "border-[#0D9488] text-[#0D9488]" : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <FileText className="w-4 h-4" /> Data Summary
        </button>

        <button
          onClick={() => setActiveTab("result")}
          className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all shrink-0 ${
            activeTab === "result" ? "border-[#0D9488] text-[#0D9488]" : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <BarChart3 className="w-4 h-4" /> Credit Result & Policy
        </button>

        <button
          onClick={() => setActiveTab("explain")}
          className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all shrink-0 ${
            activeTab === "explain" ? "border-[#0D9488] text-[#0D9488]" : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <HelpCircle className="w-4 h-4" /> Why This Decision (SHAP)
        </button>

        <button
          onClick={() => setActiveTab("whatif")}
          className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all shrink-0 ${
            activeTab === "whatif" ? "border-[#0D9488] text-[#0D9488]" : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <Sliders className="w-4 h-4" /> What-If Simulator
        </button>

        <button
          onClick={() => setActiveTab("decision")}
          className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all shrink-0 ${
            activeTab === "decision" ? "border-[#0D9488] text-[#0D9488]" : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <CheckSquare className="w-4 h-4" /> Officer Decision
        </button>

        <button
          onClick={() => setActiveTab("audit")}
          className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all shrink-0 ${
            activeTab === "audit" ? "border-[#0D9488] text-[#0D9488]" : "border-transparent text-slate-500 hover:text-slate-900"
          }`}
        >
          <History className="w-4 h-4" /> Audit Trail
        </button>
      </div>

      {/* Tab 1: Data Summary */}
      {activeTab === "summary" && (
        <div className="space-y-6">
          {analysisRun ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
                  <div className="text-xs text-slate-500 font-medium">Gross Monthly Inflow</div>
                  <div className="text-xl font-bold text-slate-900">₹{analysisRun.cashflow.gross_business_inflow_monthly?.toLocaleString()}</div>
                  <div className="text-[10px] text-slate-400">Business credits before costs</div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
                  <div className="text-xs text-slate-500 font-medium">Estimated Monthly Outflow</div>
                  <div className="text-xl font-bold text-slate-900">₹{analysisRun.cashflow.estimated_business_outflow_monthly?.toLocaleString()}</div>
                  <div className="text-[10px] text-slate-400">Operating costs & debits</div>
                </div>

                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
                  <div className="text-xs text-slate-500 font-medium">Stable Monthly Net Cash Flow</div>
                  <div className="text-xl font-bold text-emerald-700">₹{analysisRun.cashflow.stable_monthly_cash_flow?.toLocaleString()}</div>
                  <div className="text-[10px] text-slate-400">Median net monthly cash flow</div>
                </div>
              </div>

              {/* Fraud Flags Section */}
              {analysisRun.fraud_flags.length > 0 && (
                <div className="bg-white border border-amber-200 p-5 rounded-2xl shadow-sm space-y-3">
                  <div className="flex items-center gap-2 text-xs font-bold text-amber-800">
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                    <span>Data Integrity & Fraud Flags ({analysisRun.fraud_flags.length})</span>
                  </div>
                  <div className="space-y-2">
                    {analysisRun.fraud_flags.map((ff: any, idx: number) => (
                      <div key={idx} className="bg-amber-50/50 p-3 rounded-xl border border-amber-200/80 text-xs flex items-start gap-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          ff.severity === 'High' ? 'bg-rose-100 text-rose-800 border border-rose-200' : 'bg-amber-100 text-amber-900 border border-amber-300'
                        }`}>
                          {ff.severity} Severity
                        </span>
                        <div>
                          <div className="font-bold text-slate-900">{ff.flag_type}</div>
                          <div className="text-slate-600 mt-0.5">{ff.evidence_summary}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-xs text-slate-400 py-6">No analysis run uploaded for this application yet.</div>
          )}
        </div>
      )}

      {/* Tab 2: Credit Result & Policy */}
      {activeTab === "result" && analysisRun && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <ScoreGauge
            score={analysisRun.prediction.score}
            probability={analysisRun.prediction.default_probability}
            dataConfidence={analysisRun.data.data_confidence}
            scoreRange={analysisRun.prediction.score_range}
          />

          <div className="md:col-span-2 bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-6">
            <div>
              <h3 className="text-base font-bold text-slate-900">Loan Policy Recommendation</h3>
              <p className="text-xs text-slate-500">
                Calculated under prototype policy rules using lean-month cash flow and credit score multiplier.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div className="text-xs font-medium text-slate-500">Requested Loan Amount</div>
                <div className="text-xl font-extrabold text-slate-900">₹{analysisRun.loan_policy.requested_amount?.toLocaleString()}</div>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div className="text-xs font-medium text-slate-500">Recommended Loan Amount</div>
                <div className="text-xl font-extrabold text-[#0D9488]">₹{analysisRun.loan_policy.recommended_amount?.toLocaleString()}</div>
              </div>
            </div>

            {/* Affordability Analysis Grid */}
            {analysisRun.loan_policy.affordability && (
              <div className="bg-slate-50/80 border border-slate-200 p-4 rounded-xl space-y-3">
                <div className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Debt Affordability & DSCR Analysis
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-slate-500 font-medium">Est. Monthly EMI</span>
                    <div className="font-bold text-slate-900 text-sm">₹{analysisRun.loan_policy.affordability.estimated_emi_monthly?.toLocaleString()}</div>
                    <div className="text-[10px] text-slate-400">12m @ 14% p.a.</div>
                  </div>

                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-slate-500 font-medium">DSCR Ratio</span>
                    <div className="font-bold text-emerald-700 text-sm">{analysisRun.loan_policy.affordability.dscr}x</div>
                    <div className="text-[10px] text-slate-400">Target &ge; 1.25x</div>
                  </div>

                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-slate-500 font-medium">Cash Flow Ratio</span>
                    <div className="font-bold text-slate-900 text-sm">{analysisRun.loan_policy.affordability.affordability_ratio_pct}%</div>
                    <div className="text-[10px] text-slate-400">EMI / Net Cash Flow</div>
                  </div>

                  <div className="bg-white p-3 rounded-lg border border-slate-200">
                    <span className="text-slate-500 font-medium">Max Affordable EMI</span>
                    <div className="font-bold text-slate-900 text-sm">₹{analysisRun.loan_policy.affordability.max_affordable_emi_monthly?.toLocaleString()}</div>
                    <div className="text-[10px] text-slate-400">50% Net Cash Flow Cap</div>
                  </div>
                </div>
              </div>
            )}


            <div className="bg-teal-50 border border-teal-200 p-4 rounded-xl text-xs text-teal-950 space-y-1">
              <div className="font-bold text-[#0D9488] flex items-center gap-1.5">
                <Info className="w-4 h-4 shrink-0 text-[#0D9488]" /> Illustrative Prototype Policy Notice
              </div>
              <ul className="list-disc list-inside space-y-1 text-slate-700 pt-1 leading-relaxed">
                {analysisRun.loan_policy.limitations.map((lim: string, idx: number) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Why This Decision (SHAP) */}
      {activeTab === "explain" && analysisRun && (
        <ShapWaterfallChart explanations={analysisRun.explanations} />
      )}

      {/* Tab 4: What-If Simulator */}
      {activeTab === "whatif" && analysisRun && (
        <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Sliders className="w-5 h-5 text-[#0D9488]" /> Interactive Counterfactual Simulator
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Adjust plausible scenario inputs below. The system recomputes dependent cash-flow features, re-runs the trained model, and displays hypothetical score changes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-50 p-5 rounded-2xl border border-slate-200">
            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-bold mb-1">
                  Stable Monthly Net Cash Flow: ₹{whatifStable.toLocaleString()}
                </label>
                <input
                  type="range"
                  min="10000"
                  max="150000"
                  step="2500"
                  value={whatifStable}
                  onChange={(e) => setWhatifStable(Number(e.target.value))}
                  className="w-full accent-[#0D9488]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold mb-1">
                  Utility Punctuality Rate: {(whatifPunc * 100).toFixed(0)}%
                </label>
                <input
                  type="range"
                  min="0.30"
                  max="1.00"
                  step="0.05"
                  value={whatifPunc}
                  onChange={(e) => setWhatifPunc(Number(e.target.value))}
                  className="w-full accent-[#0D9488]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold mb-1">
                  Requested Loan Amount: ₹{whatifAmount.toLocaleString()}
                </label>
                <input
                  type="range"
                  min="10000"
                  max="200000"
                  step="5000"
                  value={whatifAmount}
                  onChange={(e) => setWhatifAmount(Number(e.target.value))}
                  className="w-full accent-[#0D9488]"
                />
              </div>

              <button
                onClick={handleRunWhatIf}
                disabled={whatifSimulating}
                className="w-full py-2.5 bg-[#0D9488] hover:bg-[#0F766E] text-white font-bold rounded-lg transition-all shadow-xs"
              >
                {whatifSimulating ? "Recomputing Model..." : "Simulate Scenario"}
              </button>
            </div>

            {/* What-if Output Display */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 space-y-4 shadow-xs">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">Hypothetical Simulation Result</div>

              {whatifResult ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-xs font-semibold text-slate-600">Hypothetical Score</span>
                    <div className="text-right">
                      <span className="text-xl font-bold text-slate-900">{whatifResult.hypothetical_score}</span>
                      <span className={`text-xs ml-2 font-bold ${whatifResult.score_change >= 0 ? "text-emerald-700" : "text-rose-700"}`}>
                        ({whatifResult.score_change >= 0 ? `+${whatifResult.score_change}` : whatifResult.score_change} pts)
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-xs font-semibold text-slate-600">Est. Default Probability</span>
                    <span className="text-sm font-bold text-slate-900">{(whatifResult.hypothetical_default_probability * 100).toFixed(1)}%</span>
                  </div>

                  <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-xs font-semibold text-slate-600">Hypothetical Recommended Loan</span>
                    <span className="text-sm font-bold text-[#0D9488]">₹{whatifResult.hypothetical_recommended_amount?.toLocaleString()}</span>
                  </div>

                  <p className="text-[11px] text-amber-900 bg-amber-50 p-2.5 rounded-lg border border-amber-200 leading-relaxed">
                    {whatifResult.disclaimer}
                  </p>
                </div>
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">
                  Adjust sliders on the left and click <strong>Simulate Scenario</strong> to view recomputed metrics.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Officer Review & Decision */}
      {activeTab === "decision" && (
        <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900">Loan Officer Underwriting Decision</h3>
            <p className="text-xs text-slate-500">
              Record human loan officer approval, decline, or information request. Any override of policy recommendation requires a mandatory documented rationale.
            </p>
          </div>

          {user?.role !== "officer" && (
            <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl text-xs text-amber-900 flex items-center gap-2">
              <Lock className="w-4 h-4 text-amber-700 shrink-0" />
              <span>You are logged in as a <strong>Borrower</strong>. Only authorized Loan Officers can record underwriting decisions.</span>
            </div>
          )}

          {decisionSuccess && (
            <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl text-xs text-emerald-800 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{decisionSuccess}</span>
            </div>
          )}

          {decisionError && (
            <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl text-xs text-rose-800 flex items-center gap-2">
              <XCircle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{decisionError}</span>
            </div>
          )}

          <form onSubmit={handleRecordDecision} className="space-y-4 text-xs max-w-xl">
            <div>
              <label className="block text-slate-700 font-bold mb-1">Decision Status</label>
              <select
                value={decisionStatus}
                onChange={(e) => setDecisionStatus(e.target.value)}
                disabled={user?.role !== "officer"}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5 text-slate-900 font-semibold focus:outline-none focus:border-[#0D9488]"
              >
                <option value="Approved">Approve Application</option>
                <option value="Declined">Decline Application</option>
                <option value="More Info Required">Request More Information</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-700 font-bold mb-1">Approved Loan Amount (₹)</label>
              <input
                type="number"
                value={approvedAmount}
                onChange={(e) => setApprovedAmount(Number(e.target.value))}
                disabled={user?.role !== "officer"}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5 text-slate-900 font-bold text-sm focus:outline-none focus:border-[#0D9488]"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-bold mb-1">
                Mandatory Override Reason <span className="text-slate-400 font-normal">(Required if overriding recommendation)</span>
              </label>
              <textarea
                rows={3}
                value={overrideReason}
                onChange={(e) => setOverrideReason(e.target.value)}
                placeholder="State qualitative evidence or rationale..."
                disabled={user?.role !== "officer"}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#0D9488]"
              />
            </div>

            <div>
              <label className="block text-slate-700 font-bold mb-1">Underwriting Notes</label>
              <textarea
                rows={2}
                value={decisionNotes}
                onChange={(e) => setDecisionNotes(e.target.value)}
                placeholder="Optional internal comments..."
                disabled={user?.role !== "officer"}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#0D9488]"
              />
            </div>

            <button
              type="submit"
              disabled={decisionSubmitting || user?.role !== "officer"}
              className="py-3 px-6 bg-[#0D9488] hover:bg-[#0F766E] text-white font-bold rounded-lg transition-all shadow-xs disabled:opacity-50"
            >
              {decisionSubmitting ? "Recording Decision..." : "Submit & Record Decision"}
            </button>
          </form>
        </div>
      )}

      {/* Tab 6: Audit Trail */}
      {activeTab === "audit" && (
        <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Immutable Audit Trail</h3>
            <p className="text-xs text-slate-500">
              Persistent event log tracking application creations, ML analysis runs, and officer decisions.
            </p>
          </div>

          <div className="space-y-3">
            {auditLogs.map((log) => (
              <div key={log.id} className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-[#0D9488] uppercase tracking-wider text-[11px]">{log.event_type}</span>
                  <span className="text-[11px] text-slate-500">{new Date(log.timestamp).toLocaleString()}</span>
                </div>
                <div className="text-slate-800 font-medium">
                  Actor: <strong>{log.actor_name || log.actor_id}</strong> ({log.actor_role})
                </div>
                {log.reason && (
                  <div className="text-slate-700 bg-white p-2.5 rounded border border-slate-200 mt-1">
                    Rationale: {log.reason}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

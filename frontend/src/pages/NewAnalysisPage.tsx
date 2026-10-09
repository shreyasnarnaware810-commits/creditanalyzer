import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { Upload, FileText, CheckCircle2, AlertCircle } from "lucide-react";

export const NewAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [requestedAmount, setRequestedAmount] = useState<number>(60000);
  const [txFile, setTxFile] = useState<File | null>(null);
  const [utFile, setUtFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!txFile) {
      setError("Please select or attach a transaction CSV file.");
      return;
    }
    if (!consent) {
      setError("Borrower consent is mandatory before running credit scoring analysis.");
      return;
    }

    setError(null);
    setUploading(true);

    try {
      const app = await api.createApplication(requestedAmount);
      await api.runAnalysis(app.id, txFile, utFile || undefined);
      navigate(`/applications/${app.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to complete analysis pipeline");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm">
        <h1 className="text-xl font-extrabold text-[#14243A]">
          New Credit & Cash Flow Analysis
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload consented transaction records to ingest data quality, extract cash-flow signals, run ML risk estimation, and generate SHAP explanations.
        </p>
      </div>

      {/* Main Upload Form */}
      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm space-y-6">
        {error && (
          <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl text-xs text-rose-700 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Requested Loan Amount (INR ₹)
            </label>
            <input
              type="number"
              min="5000"
              max="500000"
              step="5000"
              value={requestedAmount}
              onChange={(e) => setRequestedAmount(Number(e.target.value))}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-slate-900 font-bold text-base focus:outline-none focus:border-[#0D9488] focus:bg-white transition-colors"
            />
            <p className="text-[11px] text-slate-400 mt-1">Used for loan policy recommendation calculation.</p>
          </div>
        </div>

        {/* Transaction File Upload Box */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-2">
            1. Transaction History CSV File <span className="text-rose-600">* Mandatory</span>
          </label>

          <div className="border-2 border-dashed border-slate-200 hover:border-[#0D9488] bg-slate-50 rounded-2xl p-6 text-center transition-all">
            <input
              type="file"
              accept=".csv"
              id="tx-file-input"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setTxFile(e.target.files[0]);
                }
              }}
            />

            {txFile ? (
              <div className="flex items-center justify-center gap-3 text-emerald-700">
                <CheckCircle2 className="w-6 h-6 text-emerald-600" />
                <div className="text-left">
                  <div className="text-sm font-bold text-slate-900">{txFile.name}</div>
                  <div className="text-[11px] text-slate-500">{(txFile.size / 1024).toFixed(1)} KB • Ready for Ingestion</div>
                </div>
                <button
                  type="button"
                  onClick={() => setTxFile(null)}
                  className="text-xs text-rose-600 font-semibold underline ml-4 hover:text-rose-700"
                >
                  Change
                </button>
              </div>
            ) : (
              <label htmlFor="tx-file-input" className="cursor-pointer space-y-2 block">
                <Upload className="w-8 h-8 text-[#0D9488] mx-auto" />
                <div className="text-xs font-bold text-slate-800">
                  Click to browse transaction CSV or drag & drop file
                </div>
                <p className="text-[11px] text-slate-500 max-w-sm mx-auto">
                  Requires <code className="text-teal-700 bg-teal-50 px-1 py-0.5 rounded font-mono">transaction_date</code> and <code className="text-teal-700 bg-teal-50 px-1 py-0.5 rounded font-mono">amount</code> columns.
                </p>
              </label>
            )}
          </div>
        </div>

        {/* Utility File Upload Box (Optional) */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-2">
            2. Utility Payment History CSV File <span className="text-slate-400">(Optional)</span>
          </label>

          <div className="border border-slate-200 bg-slate-50 rounded-2xl p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-slate-400" />
              <div>
                <div className="text-xs font-semibold text-slate-800">
                  {utFile ? utFile.name : "Attach utility bill records for punctuality assessment"}
                </div>
                <p className="text-[11px] text-slate-500">Includes billing_period and payment_status.</p>
              </div>
            </div>

            <input
              type="file"
              accept=".csv"
              id="ut-file-input"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  setUtFile(e.target.files[0]);
                }
              }}
            />
            <label
              htmlFor="ut-file-input"
              className="px-3 py-1.5 rounded-lg bg-white hover:bg-slate-100 text-xs font-medium text-slate-700 border border-slate-200 cursor-pointer shadow-xs"
            >
              {utFile ? "Change" : "Browse"}
            </label>
          </div>
        </div>

        {/* Mandatory Consent Checkbox */}
        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-start gap-3">
          <input
            type="checkbox"
            id="consent-check"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            className="mt-0.5 w-4 h-4 rounded border-slate-300 text-[#0D9488] focus:ring-[#0D9488]"
          />
          <label htmlFor="consent-check" className="text-xs text-slate-700 leading-relaxed">
            <strong>Borrower Consent Granted (v1.0):</strong> I confirm explicit consent to analyze alternative financial records solely for creditworthiness evaluation under prototype policies. I understand all generated metrics are illustrative.
          </label>
        </div>

        <button
          type="submit"
          disabled={uploading}
          className="w-full py-3.5 bg-[#0D9488] hover:bg-[#0F766E] text-white font-bold text-sm rounded-xl transition-all shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>Running Pipeline & SHAP Explainer...</>
          ) : (
            <>
              <CheckCircle2 className="w-4 h-4" /> Execute Analysis Pipeline
            </>
          )}
        </button>
      </form>
    </div>
  );
};

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { Upload, FileText, CheckCircle2, AlertCircle, Download, FileSpreadsheet, Loader2, Trash2 } from "lucide-react";

interface ExtractedTransaction {
  id: number;
  transaction_date: string;
  description: string;
  transaction_type: string;
  raw_amount: number;
  signed_amount: number;
  counterparty: string;
  transaction_id: string;
  status: string;
}

interface PdfPreviewData {
  filename: string;
  row_count: number;
  valid_count: number;
  review_count: number;
  invalid_count: number;
  coverage_months: number;
  date_start: string;
  date_end: string;
  warnings: string[];
  transactions: ExtractedTransaction[];
  csv_content: string;
}

export const NewAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [requestedAmount, setRequestedAmount] = useState<number>(60000);
  const [txFile, setTxFile] = useState<File | null>(null);
  const [utFile, setUtFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // PDF Preview & Extraction State
  const [previewData, setPreviewData] = useState<PdfPreviewData | null>(null);
  const [filterType, setFilterType] = useState<"all" | "credit" | "debit" | "review">("all");

  const handleFileSelect = async (file: File) => {
    setTxFile(file);
    setError(null);
    setPreviewData(null);

    // If PDF, automatically run extraction and review step
    if (file.name.toLowerCase().endsWith(".pdf") || file.type === "application/pdf") {
      setExtracting(true);
      try {
        const res = await api.previewPdf(file);
        setPreviewData(res);
      } catch (err: any) {
        setError(err.message || "Failed to parse PDF bank statement. Please verify document formatting.");
      } finally {
        setExtracting(false);
      }
    }
  };

  const handleRemoveTxRow = (id: number) => {
    if (!previewData) return;
    const updated = previewData.transactions.filter(t => t.id !== id);
    
    // Regenerate CSV content
    const csvLines = ["transaction_date,amount"];
    let validC = 0, reviewC = 0, invalidC = 0;

    updated.forEach(t => {
      csvLines.push(`${t.transaction_date},${t.signed_amount.toFixed(2)}`);
      if (t.status === "valid") validC++;
      else if (t.status === "review") reviewC++;
      else invalidC++;
    });

    setPreviewData({
      ...previewData,
      row_count: updated.length,
      valid_count: validC,
      review_count: reviewC,
      invalid_count: invalidC,
      transactions: updated,
      csv_content: csvLines.join("\n")
    });
  };

  const handleDownloadCsv = () => {
    if (!previewData) return;
    const blob = new Blob([previewData.csv_content], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `Credence_Converted_${previewData.filename.replace(/\.pdf$/i, '')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!txFile && !previewData) {
      setError("Please select or attach a bank transaction history PDF file.");
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

      let fileToUpload: File;
      if (previewData) {
        // Create Blob CSV file from extracted & validated preview data
        const blob = new Blob([previewData.csv_content], { type: "text/csv" });
        fileToUpload = new File([blob], `${txFile?.name.replace(/\.pdf$/i, '')}_converted.csv`, { type: "text/csv" });
      } else {
        fileToUpload = txFile!;
      }

      await api.runAnalysis(app.id, fileToUpload, utFile || undefined);
      navigate(`/applications/${app.id}`);
    } catch (err: any) {
      setError(err.message || "Failed to complete analysis pipeline");
    } finally {
      setUploading(false);
    }
  };

  const filteredTransactions = previewData?.transactions.filter(t => {
    if (filterType === "credit") return t.transaction_type === "credit";
    if (filterType === "debit") return t.transaction_type === "debit";
    if (filterType === "review") return t.status === "review" || t.status === "invalid";
    return true;
  }) || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm">
        <h1 className="text-xl font-extrabold text-[#14243A]">
          New Credit & Cash Flow Analysis
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload consented PDF bank statements to extract transactions, convert them to standard CSV format, assess cash flow signals, run ML credit risk scoring, and generate SHAP explanations.
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

        {/* Transaction History PDF File Upload Box */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            1. Transaction History PDF File <span className="text-rose-600">* Mandatory</span>
          </label>
          <p className="text-[11px] text-slate-500 mb-2">
            Upload your bank account transaction history as a PDF. Credence AI will extract the transactions, convert them into the required CSV format, and use the validated data for credit analysis.
          </p>

          <div className="border-2 border-dashed border-slate-200 hover:border-[#0D9488] bg-slate-50 rounded-2xl p-6 text-center transition-all">
            <input
              type="file"
              accept=".pdf,.csv"
              id="tx-file-input"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileSelect(e.target.files[0]);
                }
              }}
            />

            {extracting ? (
              <div className="py-4 space-y-3">
                <Loader2 className="w-8 h-8 text-[#0D9488] animate-spin mx-auto" />
                <div className="text-xs font-bold text-slate-800">
                  Extracting Transactions & Normalizing PDF Layout...
                </div>
                <p className="text-[11px] text-slate-500">Parsing dates, amounts, credit/debit directions, and descriptions.</p>
              </div>
            ) : txFile ? (
              <div className="flex items-center justify-between bg-white p-4 rounded-xl border border-slate-200">
                <div className="flex items-center gap-3 text-left">
                  <FileText className="w-8 h-8 text-[#0D9488] shrink-0" />
                  <div>
                    <div className="text-sm font-bold text-slate-900">{txFile.name}</div>
                    <div className="text-[11px] text-slate-500 font-mono">
                      {(txFile.size / 1024).toFixed(1)} KB • {previewData ? `${previewData.row_count} Transactions Extracted` : "Ready"}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setTxFile(null);
                      setPreviewData(null);
                    }}
                    className="text-xs text-rose-600 font-semibold px-3 py-1.5 rounded-lg border border-rose-200 hover:bg-rose-50 transition-colors"
                  >
                    Remove
                  </button>
                  <label
                    htmlFor="tx-file-input"
                    className="text-xs text-slate-700 font-semibold px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 cursor-pointer transition-colors"
                  >
                    Change File
                  </label>
                </div>
              </div>
            ) : (
              <label htmlFor="tx-file-input" className="cursor-pointer space-y-2 block py-2">
                <Upload className="w-8 h-8 text-[#0D9488] mx-auto" />
                <div className="text-xs font-bold text-slate-800">
                  Click to browse bank statement PDF or drag & drop file here
                </div>
                <p className="text-[11px] text-slate-500 max-w-md mx-auto leading-relaxed">
                  Supports Google Pay transaction statements and standard bank statement PDFs (<code className="text-teal-700 bg-teal-50 px-1 py-0.5 rounded font-mono">.pdf</code>).
                </p>
              </label>
            )}
          </div>
        </div>

        {/* Transaction Extraction & Review Step */}
        {previewData && (
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <FileSpreadsheet className="w-5 h-5 text-[#0D9488]" />
                  <h3 className="text-sm font-extrabold text-slate-900">
                    Transaction Extraction & CSV Validation Review
                  </h3>
                </div>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Review normalized transaction records extracted from your PDF bank statement.
                </p>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  type="button"
                  onClick={handleDownloadCsv}
                  className="px-3.5 py-2 bg-white border border-slate-300 hover:bg-slate-100 text-slate-800 font-bold text-xs rounded-xl flex items-center gap-1.5 transition-colors shadow-xs"
                >
                  <Download className="w-3.5 h-3.5 text-[#0D9488]" />
                  Download Converted CSV
                </button>
              </div>
            </div>

            {/* Extracted Metrics Summary */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-white p-3 rounded-xl border border-slate-200">
                <div className="text-[10px] uppercase font-bold text-slate-400">Extracted Rows</div>
                <div className="text-lg font-black text-slate-900 mt-0.5">{previewData.row_count}</div>
              </div>
              <div className="bg-white p-3 rounded-xl border border-slate-200">
                <div className="text-[10px] uppercase font-bold text-emerald-600">Valid Rows</div>
                <div className="text-lg font-black text-emerald-700 mt-0.5">{previewData.valid_count}</div>
              </div>
              <div className="bg-white p-3 rounded-xl border border-slate-200">
                <div className="text-[10px] uppercase font-bold text-amber-600">Needs Review</div>
                <div className="text-lg font-black text-amber-700 mt-0.5">{previewData.review_count}</div>
              </div>
              <div className="bg-white p-3 rounded-xl border border-slate-200">
                <div className="text-[10px] uppercase font-bold text-teal-600">History Coverage</div>
                <div className="text-sm font-bold text-slate-800 mt-1">
                  {previewData.coverage_months} Mos ({previewData.date_start.slice(0,7)} to {previewData.date_end.slice(0,7)})
                </div>
              </div>
            </div>

            {previewData.warnings.length > 0 && (
              <div className="bg-amber-50 border border-amber-200 p-3 rounded-xl text-xs text-amber-800 space-y-1">
                {previewData.warnings.map((w, idx) => (
                  <div key={idx} className="flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                    <span>{w}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Table Filters */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1 text-xs">
                <span className="text-slate-500 font-medium mr-2">Filter:</span>
                {(["all", "credit", "debit", "review"] as const).map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setFilterType(t)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold capitalize transition-colors ${
                      filterType === t
                        ? "bg-[#0D9488] text-white"
                        : "bg-white text-slate-600 hover:bg-slate-200 border border-slate-200"
                    }`}
                  >
                    {t === "all" ? "All Records" : t}
                  </button>
                ))}
              </div>

              <div className="text-[11px] text-slate-500">
                Showing {filteredTransactions.length} of {previewData.row_count} records
              </div>
            </div>

            {/* Transaction Data Preview Table */}
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden max-h-64 overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-100 text-slate-600 font-bold sticky top-0 border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">#</th>
                    <th className="py-2.5 px-3">Date (YYYY-MM-DD)</th>
                    <th className="py-2.5 px-3">Description</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3 text-right">Raw Amount (₹)</th>
                    <th className="py-2.5 px-3 text-right">Normalized CSV Value</th>
                    <th className="py-2.5 px-3 text-center">Status</th>
                    <th className="py-2.5 px-3 text-center">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredTransactions.map((tx) => (
                    <tr key={tx.id} className="hover:bg-slate-50 transition-colors">
                      <td className="py-2 px-3 text-slate-400 font-mono text-[11px]">{tx.id}</td>
                      <td className="py-2 px-3 font-mono font-medium text-slate-800">{tx.transaction_date}</td>
                      <td className="py-2 px-3 max-w-[200px] truncate text-slate-700" title={tx.description}>
                        {tx.description}
                      </td>
                      <td className="py-2 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase ${
                            tx.transaction_type === "credit"
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-rose-100 text-rose-800"
                          }`}
                        >
                          {tx.transaction_type}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-right font-mono font-bold text-slate-800">
                        ₹{tx.raw_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                      </td>
                      <td
                        className={`py-2 px-3 text-right font-mono font-bold ${
                          tx.signed_amount >= 0 ? "text-emerald-700" : "text-rose-700"
                        }`}
                      >
                        {tx.signed_amount >= 0 ? `+${tx.signed_amount.toFixed(2)}` : tx.signed_amount.toFixed(2)}
                      </td>
                      <td className="py-2 px-3 text-center">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            tx.status === "valid"
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                              : "bg-amber-50 text-amber-700 border border-amber-200"
                          }`}
                        >
                          {tx.status}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-center">
                        <button
                          type="button"
                          onClick={() => handleRemoveTxRow(tx.id)}
                          className="text-slate-400 hover:text-rose-600 transition-colors"
                          title="Remove row"
                        >
                          <Trash2 className="w-3.5 h-3.5 mx-auto" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

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
          disabled={uploading || extracting}
          className="w-full py-3.5 bg-[#0D9488] hover:bg-[#0F766E] text-white font-bold text-sm rounded-xl transition-all shadow-sm disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {uploading ? (
            <>Running Pipeline & SHAP Explainer...</>
          ) : (
            <>
              <CheckCircle2 className="w-4 h-4" /> Confirm & Execute Analysis Pipeline
            </>
          )}
        </button>
      </form>
    </div>
  );
};

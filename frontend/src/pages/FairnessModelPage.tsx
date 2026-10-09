import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { Scale, AlertCircle } from "lucide-react";

export const FairnessModelPage: React.FC = () => {
  const [fairnessData, setFairnessData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getFairness()
      .then((data) => setFairnessData(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-white border border-slate-200 p-6 rounded-2xl shadow-sm">
        <h1 className="text-xl font-extrabold text-[#14243A] flex items-center gap-2">
          <Scale className="w-5 h-5 text-[#0D9488]" /> Fairness & Model Monitoring Diagnostic Panel
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Synthetic benchmark metrics across documented borrower archetypes. This panel evaluates group approval parity and disparate impact ratio.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12 text-xs text-slate-400">Computing synthetic fairness benchmarks...</div>
      ) : fairnessData ? (
        <>
          {/* Overview Disparate Impact Metric Card */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
              <div className="text-xs font-medium text-slate-500">Disparate Impact Ratio</div>
              <div className="text-2xl font-black text-[#0D9488]">
                {fairnessData.overall_disparate_impact}
              </div>
              <div className="text-[10px] text-slate-400">Screening benchmark ratio (&ge; 0.80 standard threshold)</div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
              <div className="text-xs font-medium text-slate-500">Model Version</div>
              <div className="text-xl font-bold font-mono text-slate-900">{fairnessData.model_version}</div>
              <div className="text-[10px] text-slate-400">GradientBoostingClassifier</div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
              <div className="text-xs font-medium text-slate-500">Evaluation Dataset</div>
              <div className="text-xl font-bold text-slate-900">{fairnessData.dataset_identifier}</div>
              <div className="text-[10px] text-slate-400">5,000 synthetic borrowers</div>
            </div>
          </div>

          {/* Group Fairness Table */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
            <h2 className="text-base font-bold text-slate-900">Group Approval & Performance Breakdown</h2>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                    <th className="py-3 px-4">Borrower Archetype</th>
                    <th className="py-3 px-4">Sample Size</th>
                    <th className="py-3 px-4">Approval Rate (&ge; 600)</th>
                    <th className="py-3 px-4">Mean Score</th>
                    <th className="py-3 px-4">Group AUC</th>
                    <th className="py-3 px-4">Disparate Impact Ratio</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {fairnessData.groups.map((g: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-50/80">
                      <td className="py-3.5 px-4 font-bold text-slate-900">{g.group_name}</td>
                      <td className="py-3.5 px-4 text-slate-500">{g.sample_count}</td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">{(g.approval_rate * 100).toFixed(1)}%</td>
                      <td className="py-3.5 px-4 font-mono font-bold text-slate-900">{g.score_average}</td>
                      <td className="py-3.5 px-4 text-slate-600 font-medium">{g.auc}</td>
                      <td className="py-3.5 px-4 font-mono font-bold text-[#0D9488]">{g.disparate_impact_ratio}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Mandatory Disclaimer Box */}
          <div className="bg-amber-50 border border-amber-200 p-5 rounded-2xl text-xs text-amber-900 space-y-2 shadow-xs">
            <div className="font-bold text-amber-800 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-600" /> Mandatory Synthetic Fairness Disclaimer
            </div>
            <p className="text-amber-900/90 leading-relaxed">
              {fairnessData.disclaimer}
            </p>
          </div>
        </>
      ) : null}
    </div>
  );
};

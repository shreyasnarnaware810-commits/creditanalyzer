import React from "react";
import { TrendingUp, TrendingDown, Info } from "lucide-react";

export interface ExplanationItem {
  feature_name: string;
  feature_value: number;
  contribution: number;
  direction: "positive" | "negative";
  technical_text: string;
  borrower_text: string;
}

interface ShapWaterfallChartProps {
  explanations: ExplanationItem[];
}

export const ShapWaterfallChart: React.FC<ShapWaterfallChartProps> = ({ explanations }) => {
  const maxAbsContribution = Math.max(...explanations.map((e) => Math.abs(e.contribution)), 10);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h3 className="text-base font-bold text-slate-900">Genuine SHAP Model Explanations</h3>
          <p className="text-xs text-slate-500">
            Feature contributions mathematically reconciled to trained model default log-odds space and converted to score points.
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <span className="flex items-center gap-1.5 text-emerald-700 font-semibold">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Positive Impact (+Score)
          </span>
          <span className="flex items-center gap-1.5 text-rose-700 font-semibold">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> Negative Impact (-Score)
          </span>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-5 space-y-3 shadow-sm">
        {explanations.map((item, idx) => {
          const isPos = item.contribution >= 0;
          const widthPct = Math.min(100, (Math.abs(item.contribution) / maxAbsContribution) * 100);

          return (
            <div
              key={idx}
              className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 hover:border-slate-300 transition-all space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {isPos ? (
                    <TrendingUp className="w-4 h-4 text-emerald-600 shrink-0" />
                  ) : (
                    <TrendingDown className="w-4 h-4 text-rose-600 shrink-0" />
                  )}
                  <span className="text-sm font-semibold text-slate-900 capitalize">
                    {item.feature_name.replace(/_/g, " ")}
                  </span>
                </div>
                <div className="text-right flex items-center gap-3">
                  <span className="text-xs text-slate-500 font-mono">
                    Val: <strong className="text-slate-900 font-sans">{typeof item.feature_value === 'number' ? item.feature_value.toLocaleString() : item.feature_value}</strong>
                  </span>
                  <span
                    className={`text-xs font-bold px-2.5 py-0.5 rounded-md ${
                      isPos
                        ? "bg-emerald-100 text-emerald-800 border border-emerald-200"
                        : "bg-rose-100 text-rose-800 border border-rose-200"
                    }`}
                  >
                    {isPos ? `+${item.contribution.toFixed(1)} pts` : `${item.contribution.toFixed(1)} pts`}
                  </span>
                </div>
              </div>

              {/* Contribution Bar */}
              <div className="w-full bg-slate-200/70 rounded-full h-2 overflow-hidden flex items-center">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    isPos ? "bg-emerald-500" : "bg-rose-500"
                  }`}
                  style={{ width: `${Math.max(5, widthPct)}%` }}
                ></div>
              </div>

              {/* Borrower Friendly Text */}
              <div className="text-xs text-slate-600 flex items-start gap-2 pt-0.5">
                <Info className="w-4 h-4 text-teal-600 shrink-0 mt-0.5" />
                <span className="leading-relaxed">{item.borrower_text}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

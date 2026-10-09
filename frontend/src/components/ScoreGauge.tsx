import React from "react";

interface ScoreGaugeProps {
  score: number;
  probability: number;
  dataConfidence: string;
  scoreRange: { low: number; high: number; type: string };
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  probability,
  dataConfidence,
  scoreRange,
}) => {
  const percentage = Math.min(100, Math.max(0, ((score - 300) / 600) * 100));

  let colorClass = "text-emerald-700 border-emerald-200 bg-emerald-50";
  let barColor = "#0D9488"; // Teal primary
  let categoryLabel = "Good Credit Tier";

  if (score < 500) {
    colorClass = "text-rose-700 border-rose-200 bg-rose-50";
    barColor = "#E11D48";
    categoryLabel = "High Risk Tier";
  } else if (score < 650) {
    colorClass = "text-amber-800 border-amber-200 bg-amber-50";
    barColor = "#D97706";
    categoryLabel = "Moderate Risk Tier";
  }

  return (
    <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col items-center justify-between text-center relative">
      <div className="w-full flex items-center justify-between text-xs text-slate-500 mb-2">
        <span className="font-bold uppercase tracking-wider text-[10px] text-slate-400">Alternative Credit Score</span>
        <span className={`px-2.5 py-0.5 rounded-full border text-[11px] font-semibold ${colorClass}`}>
          {categoryLabel}
        </span>
      </div>

      <div className="relative w-48 h-48 my-4 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="42"
            stroke="#F1F5F9"
            strokeWidth="10"
            fill="transparent"
          />
          <circle
            cx="50"
            cy="50"
            r="42"
            stroke={barColor}
            strokeWidth="10"
            strokeDasharray={264}
            strokeDashoffset={264 - (264 * percentage) / 100}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-extrabold text-slate-900 tracking-tight">{score}</span>
          <span className="text-xs text-slate-500 mt-0.5 font-medium">Scale 300 – 900</span>
          <div className="mt-2 px-2.5 py-0.5 rounded-md bg-slate-100 border border-slate-200 text-[10px] text-slate-600 font-medium">
            Heuristic Range: <strong className="text-slate-900">{scoreRange.low} – {scoreRange.high}</strong>
          </div>
        </div>
      </div>

      <div className="w-full grid grid-cols-2 gap-2 mt-2 pt-4 border-t border-slate-100 text-left">
        <div>
          <div className="text-[11px] font-medium text-slate-400">Est. Default Probability</div>
          <div className="text-base font-bold text-slate-900">{(probability * 100).toFixed(1)}%</div>
          <div className="text-[10px] text-slate-500">Synthetic estimate</div>
        </div>
        <div>
          <div className="text-[11px] font-medium text-slate-400">Data Confidence</div>
          <div className="text-base font-bold text-slate-900">{dataConfidence}</div>
          <div className="text-[10px] text-slate-500">Quality rating</div>
        </div>
      </div>
    </div>
  );
};

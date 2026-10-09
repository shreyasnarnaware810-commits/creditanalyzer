import React from "react";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

interface DataQualityBadgeProps {
  level: "High" | "Medium" | "Low" | string;
  warnings?: string[];
}

export const DataQualityBadge: React.FC<DataQualityBadgeProps> = ({ level, warnings = [] }) => {
  let badgeStyle = "bg-emerald-50 text-emerald-700 border-emerald-200";
  let Icon = CheckCircle2;

  if (level === "Medium") {
    badgeStyle = "bg-amber-50 text-amber-800 border-amber-200";
    Icon = AlertTriangle;
  } else if (level === "Low") {
    badgeStyle = "bg-rose-50 text-rose-700 border-rose-200";
    Icon = XCircle;
  }

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold ${badgeStyle}`}>
        <Icon className="w-3.5 h-3.5" />
        <span>Data Quality: {level}</span>
      </div>
      {warnings.length > 0 && (
        <div className="text-[11px] text-amber-900 bg-amber-50 p-2.5 rounded-lg border border-amber-200 mt-1 max-w-md">
          <div className="font-semibold mb-0.5 text-amber-800">Quality Warnings ({warnings.length}):</div>
          <ul className="list-disc list-inside space-y-0.5 text-amber-900/90">
            {warnings.map((w, idx) => (
              <li key={idx}>{w}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

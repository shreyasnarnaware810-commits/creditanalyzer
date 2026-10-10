import React from "react";
import { AlertCircle } from "lucide-react";

export const DisclaimerBanner: React.FC = () => {
  return (
    <div className="bg-amber-50 border-b border-amber-200/80 px-4 py-2 text-xs text-amber-900 flex items-center justify-between">
      <div className="flex items-center gap-2 max-w-7xl mx-auto font-medium">
        <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
        <span>
          <strong>Prototype Notice:</strong> All credit outcomes, risk probabilities, loan recommendations, and fairness metrics are generated from <strong>synthetic data</strong> for demonstration purposes. They do not constitute real lending offers or underwriting advice.
        </span>
      </div>
    </div>
  );
};

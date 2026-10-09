import shap
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple
from app.services.ml_engine import ml_engine, FACTOR, FEATURE_NAMES

class SHAPExplainerService:
    def __init__(self):
        self.explainer = shap.TreeExplainer(ml_engine.model)

    def explain(self, feature_dict: Dict[str, float]) -> List[Dict[str, Any]]:
        row = [feature_dict.get(col, 0.0) for col in FEATURE_NAMES]
        df = pd.DataFrame([row], columns=FEATURE_NAMES)
        
        raw_shap = self.explainer.shap_values(df)
        
        # Robust handling of SHAP expected_value
        exp_val = np.asarray(self.explainer.expected_value).ravel()
        if len(exp_val) > 1:
            base_logodds = float(exp_val[1])
        else:
            base_logodds = float(exp_val[0])
        
        # Robust handling of SHAP shap_values
        if isinstance(raw_shap, list):
            # Binary classifier returns list [class 0 array, class 1 array]
            if len(raw_shap) > 1:
                shap_vec = raw_shap[1][0]
            else:
                shap_vec = raw_shap[0][0]
        elif isinstance(raw_shap, np.ndarray):
            if len(raw_shap.shape) == 3:
                shap_vec = raw_shap[0, :, 1]
            elif len(raw_shap.shape) == 2:
                shap_vec = raw_shap[0]
            else:
                shap_vec = raw_shap.ravel()
        else:
            shap_vec = np.array(raw_shap).ravel()

        explanations = []
        for idx, col in enumerate(FEATURE_NAMES):
            val = float(feature_dict.get(col, 0.0))
            shap_val = float(shap_vec[idx])
            score_pts = float(-shap_val * FACTOR)
            direction = "positive" if score_pts >= 0 else "negative"
            
            tech_text, borrower_text = self._generate_explanation_text(col, val, score_pts)
            
            explanations.append({
                "feature_name": col,
                "feature_value": val,
                "contribution": round(score_pts, 2),
                "logodds_contribution": round(shap_val, 4),
                "output_space": "score_points",
                "direction": direction,
                "technical_text": tech_text,
                "borrower_text": borrower_text
            })
            
        explanations.sort(key=lambda x: abs(x["contribution"]), reverse=True)
        return explanations

    def _generate_explanation_text(self, feature_name: str, val: float, pts: float) -> Tuple[str, str]:
        sign_str = "+" if pts >= 0 else ""
        pts_round = int(round(pts))
        
        if feature_name == "stable_monthly_cash_flow":
            tech = f"Stable monthly net cash flow of ₹{val:,.0f} contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"Your steady monthly cash flow of ₹{val:,.0f} demonstrates strong repayment capacity and boosted your score."
            else:
                borr = f"Your recorded monthly cash flow of ₹{val:,.0f} is lower than ideal for this loan size, reducing your score."
                
        elif feature_name == "lean_month_cash_flow":
            tech = f"Lean-month cash flow buffer of ₹{val:,.0f} contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"Even in your lowest-earning month (₹{val:,.0f}), you maintained positive cash flow to cover debt service."
            else:
                borr = f"In low-activity months, cash flow dropped to ₹{val:,.0f}, creating liquidity risk during lean periods."
                
        elif feature_name == "income_volatility":
            tech = f"Income volatility coefficient of {val:.2f} contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"Your cash flow was relatively stable month-to-month, making your business income predictable."
            else:
                borr = f"Your cash flow fluctuated significantly month-to-month ({val*100:.0f}% volatility), raising risk concerns."
                
        elif feature_name == "activity_regularity":
            tech = f"Business activity regularity ratio of {val*100:.0f}% contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"You had consistent business transactions across {val*100:.0f}% of observed weeks."
            else:
                borr = f"Infrequent or sporadic business transactions ({val*100:.0f}% active weeks) reduced score confidence."
                
        elif feature_name == "counterparty_concentration":
            tech = f"Counterparty concentration ratio of {val*100:.0f}% contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"Your revenue is diversified across multiple customers, reducing dependence on a single client."
            else:
                borr = f"A large share of business payments ({val*100:.0f}%) comes from a single customer, creating concentration risk."
                
        elif feature_name == "utility_payment_punctuality":
            tech = f"Utility payment punctuality rate of {val*100:.0f}% contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"Excellent on-time utility bill payment record ({val*100:.0f}%) positively supported your credit estimate."
            else:
                borr = f"Overdue or late utility bill payments ({val*100:.0f}% on-time rate) negatively impacted your score."
                
        elif feature_name == "month_end_buffer":
            tech = f"Month-end reserve buffer ratio of {val:.2f} contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"Healthy month-end bank balance buffer relative to outflows provided liquidity protection."
            else:
                borr = f"Thin month-end balance buffer left limited margin for unexpected expenses."
                
        elif feature_name == "history_months":
            tech = f"Recorded history of {val:.1f} months contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"A solid history of {val:.0f} months of banking records provided strong evidence of consistency."
            else:
                borr = f"A limited transaction history ({val:.1f} months) reduces model certainty."
                
        elif feature_name == "recent_inflow_spike_ratio":
            tech = f"Recent inflow spike ratio of {val:.2f} contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"Recent cash inflow was consistent with historical business trends."
            else:
                borr = f"An unusual spike in recent inflows ({val:.1f}x normal) triggered a caution flag."
                
        elif feature_name == "round_number_ratio":
            tech = f"Round-number transaction ratio of {val*100:.0f}% contributed {sign_str}{pts_round} score points."
            if pts >= 0:
                borr = f"Transaction amount patterns resemble normal commercial sales activity."
            else:
                borr = f"High proportion of round-number transfers ({val*100:.0f}%) prompted additional review."
                
        else:
            tech = f"Feature {feature_name} (value: {val:.2f}) contributed {sign_str}{pts_round} score points."
            borr = f"Feature {feature_name} influenced your credit score estimate by {sign_str}{pts_round} points."
            
        return tech, borr

shap_explainer = SHAPExplainerService()

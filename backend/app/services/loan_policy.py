from typing import Dict, Any

def evaluate_loan_policy(
    score: int,
    lean_month_cash_flow: float,
    requested_amount: float,
    data_confidence: str = "Medium",
    fraud_risk_level: str = "None"
) -> Dict[str, Any]:
    
    # 1. Multiplier lookup based on prototype score thresholds
    if score >= 700:
        multiplier = 3.0
    elif score >= 600:
        multiplier = 2.0
    elif score >= 500:
        multiplier = 1.0
    else:
        multiplier = 0.0
        
    capacity = max(0.0, lean_month_cash_flow) * multiplier
    
    # Cap at requested amount
    recommended = min(capacity, requested_amount)
    
    limitations = [
        "Illustrative prototype recommendation based on decision-support outputs and rules; not a binding lending offer.",
        "Loan calculation scales lean-month cash flow by score tiers."
    ]
    
    if data_confidence == "Low" or fraud_risk_level == "High":
        status = "More Info Required"
        recommended = round(recommended * 0.5, -2) # Conservative scaling
        limitations.append("Recommended amount reduced due to low data confidence or active data quality flags.")
    elif score < 500:
        status = "Decline Suggested"
        recommended = 0.0
    else:
        status = "Approved Suggested"
        
    recommended = round(max(0.0, recommended), -2) # Round to nearest 100

    # 2. Affordability Analysis
    # Standard 12-month micro-loan @ 14% p.a.
    annual_rate = 0.14
    monthly_rate = annual_rate / 12
    tenure_months = 12

    if recommended > 0:
        # Standard annuity EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        pow_val = (1 + monthly_rate) ** tenure_months
        estimated_emi = round(recommended * monthly_rate * pow_val / (pow_val - 1), 2)
    else:
        estimated_emi = 0.0

    # DSCR = Net Stable Monthly Cash Flow / Estimated EMI
    stable_cf = max(1.0, lean_month_cash_flow)
    if estimated_emi > 0:
        dscr = round(stable_cf / estimated_emi, 2)
        affordability_ratio = round((estimated_emi / stable_cf) * 100, 1)
    else:
        dscr = 0.0
        affordability_ratio = 0.0

    max_affordable_emi = round(stable_cf * 0.50, 2)
    
    return {
        "requested_amount": float(requested_amount),
        "recommended_amount": float(recommended),
        "policy_version": "demo_policy_v1",
        "recommendation_status": status,
        "multiplier": multiplier,
        "limitations": limitations,
        "affordability": {
            "estimated_emi_monthly": estimated_emi,
            "dscr": dscr,
            "affordability_ratio_pct": affordability_ratio,
            "max_affordable_emi_monthly": max_affordable_emi,
            "tenure_months": tenure_months,
            "annual_interest_rate_pct": 14.0
        }
    }


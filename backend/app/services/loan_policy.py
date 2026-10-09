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
        "Illustrative prototype recommendation based on synthetic-model outputs and simplified rules; not a verified lending offer.",
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
    
    return {
        "requested_amount": float(requested_amount),
        "recommended_amount": float(recommended),
        "policy_version": "demo_policy_v1",
        "recommendation_status": status,
        "multiplier": multiplier,
        "limitations": limitations
    }

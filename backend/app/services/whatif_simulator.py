from typing import Dict, Any
from app.services.ml_engine import ml_engine
from app.services.loan_policy import evaluate_loan_policy

def simulate_whatif_scenario(
    original_features: Dict[str, float],
    original_score: int,
    original_prob: float,
    original_recommended_amount: float,
    data_confidence: str,
    overrides: Dict[str, Any]
) -> Dict[str, Any]:
    
    simulated_features = original_features.copy()
    changed_inputs = {}
    
    # 1. Update stable cash flow
    if overrides.get("stable_cash_flow") is not None:
        new_stable = float(overrides["stable_cash_flow"])
        old_stable = simulated_features.get("stable_monthly_cash_flow", 1.0)
        ratio = new_stable / old_stable if old_stable > 0 else 1.0
        
        simulated_features["stable_monthly_cash_flow"] = new_stable
        # Recompute dependent lean month cash flow proportionally
        simulated_features["lean_month_cash_flow"] = round(simulated_features.get("lean_month_cash_flow", 0.0) * ratio, 2)
        simulated_features["gross_business_inflow_monthly"] = round(simulated_features.get("gross_business_inflow_monthly", 0.0) * ratio, 2)
        changed_inputs["stable_monthly_cash_flow"] = {"from": old_stable, "to": new_stable}

    # 2. Update utility payment punctuality
    if overrides.get("utility_punctuality") is not None:
        new_punc = float(overrides["utility_punctuality"])
        old_punc = simulated_features.get("utility_payment_punctuality", 0.75)
        simulated_features["utility_payment_punctuality"] = new_punc
        changed_inputs["utility_payment_punctuality"] = {"from": old_punc, "to": new_punc}

    # 3. Update month end buffer
    if overrides.get("month_end_buffer") is not None:
        new_buf = float(overrides["month_end_buffer"])
        old_buf = simulated_features.get("month_end_buffer", 0.8)
        simulated_features["month_end_buffer"] = new_buf
        changed_inputs["month_end_buffer"] = {"from": old_buf, "to": new_buf}

    # Re-run ML model prediction
    pred = ml_engine.predict(simulated_features, data_confidence=data_confidence)
    hypo_score = pred["score"]
    hypo_prob = pred["default_probability"]
    
    # Re-evaluate policy
    requested = float(overrides.get("requested_amount") or original_features.get("requested_amount", 50000))
    policy_res = evaluate_loan_policy(
        score=hypo_score,
        lean_month_cash_flow=simulated_features["lean_month_cash_flow"],
        requested_amount=requested,
        data_confidence=data_confidence
    )
    
    score_change = hypo_score - original_score
    prob_change = round(hypo_prob - original_prob, 4)
    
    return {
        "original_analysis_run_id": overrides.get("analysis_run_id", ""),
        "hypothetical_score": hypo_score,
        "score_change": score_change,
        "hypothetical_default_probability": hypo_prob,
        "probability_change": prob_change,
        "original_recommended_amount": original_recommended_amount,
        "hypothetical_recommended_amount": policy_res["recommended_amount"],
        "changed_inputs": changed_inputs,
        "disclaimer": "Illustration only: Under the prototype model, hypothetical changes in cash flow or punctuality update the estimated score. This scenario does not guarantee loan eligibility or approval."
    }

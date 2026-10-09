from typing import Dict, Any, List, Tuple

def evaluate_fraud_heuristics(features: Dict[str, Any], duplicate_count: int = 0) -> Tuple[List[Dict[str, str]], str]:
    flags = []
    
    # 1. Inflow Spike Check
    spike_ratio = features.get("recent_inflow_spike_ratio", 1.0)
    if spike_ratio > 2.5:
        flags.append({
            "flag_type": "Recent Inflow Spike",
            "severity": "High",
            "evidence_summary": f"Recent monthly inflow is {spike_ratio:.1f}x higher than historical average. Requires verification against invoice records."
        })
    elif spike_ratio > 1.8:
        flags.append({
            "flag_type": "Recent Inflow Spike",
            "severity": "Medium",
            "evidence_summary": f"Recent monthly inflow increased by {spike_ratio:.1f}x compared to baseline."
        })
        
    # 2. Counterparty Concentration Check
    concentration = features.get("counterparty_concentration", 0.0)
    if concentration > 0.75:
        flags.append({
            "flag_type": "High Counterparty Concentration",
            "severity": "Medium",
            "evidence_summary": f"Single counterparty accounts for {concentration*100:.0f}% of total business credits. Business risk is tied to single buyer."
        })
        
    # 3. Duplicate Records Check
    if duplicate_count > 0:
        flags.append({
            "flag_type": "Duplicate Transaction Records",
            "severity": "Medium" if duplicate_count > 3 else "Low",
            "evidence_summary": f"Identified {duplicate_count} duplicate transaction entries in uploaded record."
        })
        
    # 4. Round Number Pattern Check
    round_ratio = features.get("round_number_ratio", 0.0)
    if round_ratio > 0.65:
        flags.append({
            "flag_type": "Round Amount Concentration",
            "severity": "Low",
            "evidence_summary": f"{round_ratio*100:.0f}% of transactions are exact round amounts. Common in informal business, but flag for invoice spot check."
        })
        
    # 5. Short History Warning
    history_months = features.get("history_months", 12.0)
    if history_months < 6.0:
        flags.append({
            "flag_type": "Short Observation History",
            "severity": "Low",
            "evidence_summary": f"Only {history_months:.1f} months of banking records provided. Confidence range widened."
        })
        
    # Determine overall severity level
    severities = [f["severity"] for f in flags]
    if "High" in severities:
        overall_level = "High"
    elif "Medium" in severities:
        overall_level = "Medium"
    elif "Low" in severities:
        overall_level = "Low"
    else:
        overall_level = "None"
        
    return flags, overall_level

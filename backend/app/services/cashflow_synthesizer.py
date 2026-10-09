import pandas as pd
import numpy as np
from typing import Dict, Any

EXCLUDED_CATEGORIES = ["transfer", "self-transfer", "loan_disbursal", "refund", "personal"]

def compute_cashflow_features(df_tx: pd.DataFrame, punctuality_rate: float = 0.85) -> Dict[str, Any]:
    tx = df_tx.copy()
    tx["transaction_date"] = pd.to_datetime(tx["transaction_date"], errors="coerce")
    tx = tx.dropna(subset=["transaction_date", "amount"])
    
    if len(tx) == 0:
        raise ValueError("Cannot compute cash flow on empty transaction set.")
        
    # Standardize categories and descriptions
    if "category" not in tx.columns:
        tx["category"] = "unknown"
    else:
        tx["category"] = tx["category"].astype(str).str.lower().str.strip()
        
    if "description" not in tx.columns:
        tx["description"] = ""
    else:
        tx["description"] = tx["description"].astype(str).str.lower()
        
    # Exclusions
    excluded_mask = (
        tx["category"].isin(EXCLUDED_CATEGORIES) |
        tx["description"].str.contains("self transfer|loan|refund|internal", regex=True)
    )
    
    valid_tx = tx[~excluded_mask].copy()
    
    # Establish full calendar months range
    min_date = valid_tx["transaction_date"].min()
    max_date = valid_tx["transaction_date"].max()
    
    start_month = pd.Period(min_date, freq="M")
    end_month = pd.Period(max_date, freq="M")
    all_months = pd.period_range(start_month, end_month, freq="M")
    
    valid_tx["month"] = valid_tx["transaction_date"].dt.to_period("M")
    
    credits_mask = (valid_tx["transaction_type"] == "credit")
    debits_mask = (valid_tx["transaction_type"] == "debit")
    
    monthly_credits = valid_tx[credits_mask].groupby("month")["amount"].sum().reindex(all_months, fill_value=0.0)
    monthly_debits = valid_tx[debits_mask].groupby("month")["amount"].sum().reindex(all_months, fill_value=0.0)
    monthly_net = monthly_credits - monthly_debits
    
    gross_inflow = float(monthly_credits.mean())
    estimated_outflow = float(monthly_debits.mean())
    net_cash_flow = gross_inflow - estimated_outflow
    
    stable_cash_flow = float(monthly_net.median())
    lean_cash_flow = float(np.percentile(monthly_net, 25))
    
    # Volatility calculation (guarded)
    mean_net = float(monthly_net.mean())
    std_net = float(monthly_net.std()) if len(monthly_net) > 1 else 0.0
    if mean_net > 1000:
        income_volatility = float(np.clip(std_net / mean_net, 0.0, 3.0))
    else:
        income_volatility = float(np.clip(std_net / (abs(mean_net) + 5000), 0.0, 3.0))
        
    # Activity Regularity (weekly basis)
    min_week = min_date.to_period("W")
    max_week = max_date.to_period("W")
    all_weeks = pd.period_range(min_week, max_week, freq="W")
    valid_tx["week"] = valid_tx["transaction_date"].dt.to_period("W")
    active_weeks_count = valid_tx[credits_mask]["week"].nunique()
    total_weeks = len(all_weeks) if len(all_weeks) > 0 else 1
    activity_regularity = float(np.clip(active_weeks_count / total_weeks, 0.0, 1.0))
    
    # Counterparty Concentration
    if "payer_id" in valid_tx.columns and valid_tx["payer_id"].notna().sum() > 0:
        payer_sums = valid_tx[credits_mask].groupby("payer_id")["amount"].sum()
        total_credit = payer_sums.sum()
        if total_credit > 0:
            counterparty_concentration = float(payer_sums.max() / total_credit)
        else:
            counterparty_concentration = 0.25
    else:
        # Fallback from description grouping
        desc_sums = valid_tx[credits_mask].groupby("description")["amount"].sum()
        total_credit = desc_sums.sum()
        if total_credit > 0 and len(desc_sums) > 0:
            counterparty_concentration = float(desc_sums.max() / total_credit)
        else:
            counterparty_concentration = 0.25
            
    counterparty_concentration = float(np.clip(counterparty_concentration, 0.05, 0.95))
    
    # Month-end buffer estimation
    if "balance_after_transaction" in valid_tx.columns and valid_tx["balance_after_transaction"].notna().sum() > 0:
        last_balances = valid_tx.groupby("month")["balance_after_transaction"].last()
        median_balance = float(last_balances.median())
        if estimated_outflow > 0:
            month_end_buffer = float(np.clip(median_balance / estimated_outflow, 0.0, 3.0))
        else:
            month_end_buffer = 1.0
    else:
        # Proxy from net cash flow ratio
        if estimated_outflow > 0:
            month_end_buffer = float(np.clip(stable_cash_flow / estimated_outflow, 0.0, 2.5))
        else:
            month_end_buffer = 0.8
            
    # Seasonality index
    if gross_inflow > 0:
        seasonality_index = float(np.clip(monthly_credits.max() / gross_inflow, 1.0, 4.0))
    else:
        seasonality_index = 1.0
        
    # Recent inflow spike ratio
    if len(monthly_credits) >= 2:
        last_month = monthly_credits.iloc[-1]
        prior_mean = monthly_credits.iloc[:-1].mean()
        if prior_mean > 1000:
            recent_spike_ratio = float(last_month / prior_mean)
        else:
            recent_spike_ratio = 1.0
    else:
        recent_spike_ratio = 1.0
        
    # Round number ratio
    round_count = (valid_tx["amount"] % 100 == 0).sum()
    round_number_ratio = float(round_count / len(valid_tx)) if len(valid_tx) > 0 else 0.0
    
    history_months = float(len(all_months))
    
    features = {
        "stable_monthly_cash_flow": round(stable_cash_flow, 2),
        "lean_month_cash_flow": round(lean_cash_flow, 2),
        "income_volatility": round(income_volatility, 4),
        "activity_regularity": round(activity_regularity, 4),
        "counterparty_concentration": round(counterparty_concentration, 4),
        "utility_payment_punctuality": round(punctuality_rate, 4),
        "month_end_buffer": round(month_end_buffer, 2),
        "history_months": round(history_months, 1),
        "seasonality_index": round(seasonality_index, 2),
        "recent_inflow_spike_ratio": round(recent_spike_ratio, 2),
        "round_number_ratio": round(round_number_ratio, 4),
        # Additional summary metrics
        "gross_business_inflow_monthly": round(gross_inflow, 2),
        "estimated_business_outflow_monthly": round(estimated_outflow, 2),
        "estimated_net_business_cash_flow": round(net_cash_flow, 2),
        "observed_months": len(all_months),
        "missing_months": 0 # Complete calendar established
    }
    
    return features

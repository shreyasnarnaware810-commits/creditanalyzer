import io
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Tuple

REQUIRED_TRANSACTION_COLS = ["transaction_date", "amount"]
REQUIRED_UTILITY_COLS = ["billing_period", "payment_status"]

def parse_transaction_csv(file_content: bytes, filename: str) -> Dict[str, Any]:
    checksum = hashlib.sha256(file_content).hexdigest()
    
    try:
        df = pd.read_csv(io.BytesIO(file_content))
    except Exception as e:
        return {
            "status": "invalid",
            "error_message": f"Failed to parse CSV file: {str(e)}",
            "checksum": checksum,
            "filename": filename
        }
        
    cols = [str(c).strip().lower() for c in df.columns]
    df.columns = cols
    
    missing_req = [col for col in REQUIRED_TRANSACTION_COLS if col not in cols]
    if missing_req:
        return {
            "status": "invalid",
            "error_message": f"Missing required columns in transaction CSV: {missing_req}",
            "checksum": checksum,
            "filename": filename
        }
        
    # Check for canonical columns or fill defaults
    if "transaction_type" not in df.columns:
        # Infer type from sign of amount if available
        df["transaction_type"] = np.where(df["amount"] >= 0, "credit", "debit")
        df["amount"] = df["amount"].abs()
    else:
        df["transaction_type"] = df["transaction_type"].astype(str).str.lower().str.strip()
        
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.dropna(subset=["transaction_date", "amount"])
    
    if len(df) == 0:
        return {
            "status": "invalid",
            "error_message": "No valid transaction rows found after date and amount parsing.",
            "checksum": checksum,
            "filename": filename
        }
        
    # Sort chronologically
    df = df.sort_values("transaction_date").reset_index(drop=True)
    
    # Check duplicate transaction IDs or exact row duplicates
    duplicate_count = 0
    if "transaction_id" in df.columns:
        duplicate_count = int(df.duplicated(subset=["transaction_id"]).sum())
    else:
        duplicate_count = int(df.duplicated(subset=["transaction_date", "amount"]).sum())
        
    date_start = df["transaction_date"].min().strftime("%Y-%m-%d")
    date_end = df["transaction_date"].max().strftime("%Y-%m-%d")
    
    # Coverage calculation (months)
    start_dt = df["transaction_date"].min()
    end_dt = df["transaction_date"].max()
    coverage_months = round((end_dt - start_dt).days / 30.4375, 1)
    if coverage_months < 1.0:
        coverage_months = 1.0
        
    # Data Quality Assessment
    warnings = []
    if duplicate_count > 0:
        warnings.append(f"Flagged {duplicate_count} potential duplicate transaction records.")
    if coverage_months < 6.0:
        warnings.append(f"Short history observation period ({coverage_months:.1f} months). Recommended minimum is 12 months.")
    if "payer_id" not in df.columns and "payee_id" not in df.columns:
        warnings.append("Missing counterparty identifiers (payer_id/payee_id). Counterparty concentration is estimated from descriptions.")
        
    if coverage_months >= 12.0 and duplicate_count == 0:
        quality_level = "High"
    elif coverage_months >= 6.0:
        quality_level = "Medium"
    else:
        quality_level = "Low"
        
    return {
        "status": "valid" if len(warnings) == 0 else "warning",
        "quality_level": quality_level,
        "checksum": checksum,
        "filename": filename,
        "row_count": len(df),
        "duplicate_count": duplicate_count,
        "date_start": date_start,
        "date_end": date_end,
        "coverage_months": coverage_months,
        "warnings": warnings,
        "dataframe": df
    }

def parse_utility_csv(file_content: bytes, filename: str) -> Dict[str, Any]:
    checksum = hashlib.sha256(file_content).hexdigest()
    try:
        df = pd.read_csv(io.BytesIO(file_content))
    except Exception as e:
        return {
            "status": "invalid",
            "error_message": f"Failed to parse utility CSV file: {str(e)}",
            "checksum": checksum,
            "filename": filename
        }
        
    cols = [str(c).strip().lower() for c in df.columns]
    df.columns = cols
    
    missing_req = [col for col in REQUIRED_UTILITY_COLS if col not in cols]
    if missing_req:
        return {
            "status": "invalid",
            "error_message": f"Missing required columns in utility CSV: {missing_req}",
            "checksum": checksum,
            "filename": filename
        }
        
    # Calculate punctuality if due_date and payment_date exist
    punctuality_rate = None
    if "due_date" in df.columns and "payment_date" in df.columns:
        df["due_dt"] = pd.to_datetime(df["due_date"], errors="coerce")
        df["pay_dt"] = pd.to_datetime(df["payment_date"], errors="coerce")
        valid_dates = df.dropna(subset=["due_dt", "pay_dt"])
        if len(valid_dates) > 0:
            on_time = (valid_dates["pay_dt"] <= valid_dates["due_dt"]).sum()
            punctuality_rate = round(float(on_time / len(valid_dates)), 4)
            
    if punctuality_rate is None and "payment_status" in df.columns:
        status_series = df["payment_status"].astype(str).str.lower()
        paid_count = (status_series.isin(["paid", "on-time", "success"])).sum()
        if len(df) > 0:
            punctuality_rate = round(float(paid_count / len(df)), 4)
            
    return {
        "status": "valid",
        "checksum": checksum,
        "filename": filename,
        "row_count": len(df),
        "punctuality_rate": punctuality_rate if punctuality_rate is not None else 0.75,
        "dataframe": df
    }

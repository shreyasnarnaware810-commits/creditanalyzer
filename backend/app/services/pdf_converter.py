import io
import re
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from pypdf import PdfReader

def parse_pdf_bank_statement(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Extracts transaction history from a PDF bank statement using a multi-layer strategy:
    Layer 1: Format-specific Google Pay statement parser.
    Layer 2: Standard single-line tabular bank statement parser.
    Layer 3: Multi-line structured fallback parser.
    
    Normalizes records into standard DataFrame columns:
    - transaction_date
    - amount
    - transaction_type (credit / debit)
    - description / narration
    - counterparty
    - transaction_id
    - source
    """
    checksum = hashlib.sha256(file_content).hexdigest()
    
    try:
        reader = PdfReader(io.BytesIO(file_content))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text() or ""
            pages_text.append(t)
        extracted_text = "\n".join(pages_text)
    except Exception as e:
        return {
            "status": "invalid",
            "error_message": f"Failed to read PDF document: {str(e)}",
            "checksum": checksum,
            "filename": filename
        }

    # 1. Check for empty / scanned PDF
    if not extracted_text or len(extracted_text.strip()) < 20:
        return {
            "status": "invalid",
            "error_message": "This PDF appears to be scanned or contains no text layer. Text extraction failed; OCR may be required.",
            "checksum": checksum,
            "filename": filename
        }

    lines = [l.strip() for l in extracted_text.splitlines() if l.strip()]

    # Layer 1: Google Pay Parser
    records = _parse_gpay_statement(lines)

    # Layer 2: Single-line Tabular Parser (e.g. standard bank statements)
    if not records:
        records = _parse_tabular_bank_statement(lines)

    # Layer 3: Structured Multi-line Fallback Parser
    if not records:
        records = _parse_multiline_fallback_statement(lines)

    # If parsing still fails after all 3 layers
    if not records:
        return {
            "status": "invalid",
            "error_message": "The PDF contains text, but its transaction layout is not yet supported. Please upload a standard bank statement or Google Pay PDF.",
            "checksum": checksum,
            "filename": filename
        }

    df = pd.DataFrame(records)

    # Normalize dates and amounts
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["transaction_date", "amount"])
    df = df[df["amount"] > 0.001]

    if len(df) == 0:
        return {
            "status": "invalid",
            "error_message": "No valid transaction dates or non-zero amounts could be parsed from the PDF.",
            "checksum": checksum,
            "filename": filename
        }

    # Sort chronologically
    df = df.sort_values("transaction_date").reset_index(drop=True)

    # Deduplication
    if "transaction_id" in df.columns and df["transaction_id"].notna().any():
        duplicate_count = int(df.duplicated(subset=["transaction_id"]).sum())
    else:
        duplicate_count = int(df.duplicated(subset=["transaction_date", "amount", "description"]).sum())

    date_start = df["transaction_date"].min().strftime("%Y-%m-%d")
    date_end = df["transaction_date"].max().strftime("%Y-%m-%d")

    start_dt = df["transaction_date"].min()
    end_dt = df["transaction_date"].max()
    coverage_months = round((end_dt - start_dt).days / 30.4375, 1)
    if coverage_months < 1.0:
        coverage_months = 1.0

    warnings = []
    if duplicate_count > 0:
        warnings.append(f"Flagged {duplicate_count} potential duplicate transaction records from PDF extraction.")
    if coverage_months < 6.0:
        warnings.append(f"Short history observation period ({coverage_months:.1f} months) extracted from PDF.")
    
    warnings.append("Extracted from PDF bank statement using automated text parsing.")

    if coverage_months >= 12.0 and duplicate_count == 0:
        quality_level = "High"
    elif coverage_months >= 6.0:
        quality_level = "Medium"
    else:
        quality_level = "Low"

    return {
        "status": "valid",
        "quality_level": quality_level,
        "checksum": checksum,
        "filename": filename,
        "row_count": len(df),
        "duplicate_count": duplicate_count,
        "date_start": date_start,
        "date_end": date_end,
        "coverage_months": coverage_months,
        "warnings": warnings,
        "dataframe": df,
        "extracted_summary": {
            "total_records": len(df),
            "total_credits": float(df[df["transaction_type"] == "credit"]["amount"].sum()),
            "total_debits": float(df[df["transaction_type"] == "debit"]["amount"].sum())
        }
    }


def _parse_gpay_statement(lines: List[str]) -> List[Dict[str, Any]]:
    """
    Specialized parser for Google Pay Transaction Statement PDFs.
    Handles multi-line blocks where date, time, description, UPI ID, bank info, and amount appear on consecutive lines.
    """
    date_re = re.compile(r'^(\d{1,2})\s*([A-Za-z]{3}),?\s*(\d{4})$')
    time_re = re.compile(r'^(\d{1,2}:\d{2})\s*(AM|PM|am|pm)$')
    amount_re = re.compile(r'^[₹\s]*([0-9,]+(?:\.[0-9]{2})?)$')

    records = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        m_date = date_re.match(line)
        if m_date:
            day, month_str, year = m_date.groups()
            if i + 1 < n:
                m_time = time_re.match(lines[i+1])
                if m_time:
                    time_str = lines[i+1]
                    raw_date_str = f"{day} {month_str} {year} {time_str}"
                    dt_val = None
                    try:
                        dt_val = datetime.strptime(raw_date_str, "%d %b %Y %I:%M%p")
                    except Exception:
                        try:
                            dt_val = datetime.strptime(f"{day} {month_str} {year}", "%d %b %Y")
                        except Exception:
                            dt_val = None

                    desc_lines = []
                    upi_id = None
                    bank_info = None
                    amount = None

                    j = i + 2
                    while j < n and j < i + 10:
                        l = lines[j]
                        # Skip header/footer noise
                        if l.startswith("=== PAGE") or l.startswith("Transactionstatement") or l.startswith("Page") or l.startswith("Note:") or "@gmail.com" in l:
                            j += 1
                            continue
                        if l in ["Date&time Transactiondetails Amount", "Sent", "Received", "Transactiondetails"]:
                            j += 1
                            continue

                        m_amt = amount_re.match(l)
                        if m_amt and "UPITransactionID" not in l and "UPI Transaction ID" not in l:
                            try:
                                amount = float(m_amt.group(1).replace(",", ""))
                                j += 1
                                break
                            except ValueError:
                                pass

                        if "UPITransactionID:" in l or "UPI Transaction ID:" in l:
                            upi_id = l.split(":")[-1].strip()
                        elif "Paidby" in l or "Paid by" in l or ("Paidto" in l and ("Bank" in l or "7942" in l)):
                            bank_info = l
                        else:
                            desc_lines.append(l)
                        j += 1

                    raw_desc = " ".join(desc_lines)
                    if "Paidto" in raw_desc or "Paid to" in raw_desc:
                        tx_type = "debit"
                        cp = re.sub(r'^Paid\s*to\s*', '', raw_desc, flags=re.IGNORECASE).strip()
                    elif "Receivedfrom" in raw_desc or "Received from" in raw_desc:
                        tx_type = "credit"
                        cp = re.sub(r'^Received\s*from\s*', '', raw_desc, flags=re.IGNORECASE).strip()
                    else:
                        tx_type = "debit"
                        cp = raw_desc

                    if amount is not None and dt_val is not None:
                        records.append({
                            "transaction_date": dt_val,
                            "amount": abs(amount),
                            "transaction_type": tx_type,
                            "description": raw_desc or "Google Pay Payment",
                            "counterparty": cp or "UPI User",
                            "transaction_id": upi_id,
                            "source": "Google Pay Statement"
                        })
                    i = j
                    continue
        i += 1

    return records


def _parse_tabular_bank_statement(lines: List[str]) -> List[Dict[str, Any]]:
    """
    Parses single-line tabular bank statement rows where date, narration, and amounts are on one line.
    """
    date_regex = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|[A-Za-z]{3}\s+\d{1,2},?\s+\d{4})'
    records = []

    for line in lines:
        date_match = re.search(date_regex, line)
        if not date_match:
            continue

        date_val = date_match.group(1)
        remaining = line.replace(date_val, "").strip()

        # Find numbers/amounts
        num_matches = re.findall(r'[+-]?[₹\s]*\d{1,3}(?:,\d{3})*(?:\.\d{2})?', remaining)
        if not num_matches:
            continue

        clean_nums = []
        for nm in num_matches:
            c = re.sub(r'[₹\s]', '', nm).replace(",", "")
            try:
                clean_nums.append(float(c))
            except ValueError:
                pass

        if not clean_nums:
            continue

        amt = clean_nums[-1]
        if abs(amt) < 0.01:
            continue

        lower_line = line.lower()
        if "cr" in lower_line or "credit" in lower_line or "received" in lower_line or "deposit" in lower_line or amt > 0:
            tx_type = "credit"
        else:
            tx_type = "debit"

        desc = remaining
        for nm in num_matches:
            desc = desc.replace(nm, "").strip()

        records.append({
            "transaction_date": date_val,
            "amount": abs(amt),
            "transaction_type": tx_type,
            "description": desc or "Bank Statement Entry",
            "counterparty": "Bank Entry",
            "source": "PDF Bank Statement"
        })

    return records


def _parse_multiline_fallback_statement(lines: List[str]) -> List[Dict[str, Any]]:
    """
    Fallback parser for multi-line semi-structured statements where records span multiple lines.
    """
    date_regex = re.compile(r'^(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})$')
    amount_regex = re.compile(r'^[₹\s]*([0-9,]+(?:\.[0-9]{2})?)\s*(Cr|Dr|CR|DR)?$')

    records = []
    i = 0
    n = len(lines)

    while i < n:
        m_date = date_regex.match(lines[i])
        if m_date:
            date_val = m_date.group(1)
            desc_parts = []
            amount = None
            tx_type = "debit"

            j = i + 1
            while j < n and j < i + 6:
                m_amt = amount_regex.match(lines[j])
                if m_amt:
                    try:
                        amount = float(m_amt.group(1).replace(",", ""))
                        indicator = (m_amt.group(2) or "").upper()
                        if indicator == "CR":
                            tx_type = "credit"
                        elif indicator == "DR":
                            tx_type = "debit"
                        j += 1
                        break
                    except ValueError:
                        pass
                else:
                    desc_parts.append(lines[j])
                j += 1

            if amount is not None:
                desc_str = " ".join(desc_parts)
                if "credit" in desc_str.lower() or "received" in desc_str.lower():
                    tx_type = "credit"

                records.append({
                    "transaction_date": date_val,
                    "amount": abs(amount),
                    "transaction_type": tx_type,
                    "description": desc_str or "Statement Record",
                    "counterparty": desc_str or "Account Holder",
                    "source": "PDF Fallback Statement"
                })
            i = j
            continue
        i += 1

    return records

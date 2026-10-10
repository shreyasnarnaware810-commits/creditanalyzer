import uuid
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from app.models.schema import AnalysisRunResponse, WhatIfRequest, WhatIfResponse
from app.auth.security import get_current_user
from app.database import get_db
from app.services.data_ingestion import parse_transaction_csv, parse_utility_csv
from app.services.pdf_converter import parse_pdf_bank_statement
from app.services.pdf_report_generator import generate_credit_assessment_pdf
from app.services.cashflow_synthesizer import compute_cashflow_features
from app.services.fraud_heuristics import evaluate_fraud_heuristics
from app.services.ml_engine import ml_engine, MODEL_VERSION
from app.services.shap_explainer import shap_explainer
from app.services.loan_policy import evaluate_loan_policy
from app.services.whatif_simulator import simulate_whatif_scenario
from fastapi.responses import Response

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

@router.post("/preview-pdf")
async def preview_pdf_transactions(
    pdf_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Extracts transactions from an uploaded bank statement PDF, returns normalized preview records,
    and formats them into the standard 2-column CSV dataset (transaction_date,amount).
    """
    if not (pdf_file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF document.")

    content = await pdf_file.read()
    res = parse_pdf_bank_statement(content, pdf_file.filename)

    if res["status"] == "invalid":
        raise HTTPException(status_code=400, detail=res["error_message"])

    df = res["dataframe"]
    csv_lines = ["transaction_date,amount"]
    transactions = []

    valid_count = 0
    review_count = 0
    invalid_count = 0

    for idx, row in df.iterrows():
        d_str = row["transaction_date"].strftime("%Y-%m-%d")
        amt = float(row["amount"])
        tx_type = str(row.get("transaction_type", "debit")).lower()
        signed_amt = amt if tx_type == "credit" else -amt

        csv_lines.append(f"{d_str},{signed_amt:.2f}")

        row_status = "valid"
        if amt <= 0 or not d_str:
            row_status = "invalid"
            invalid_count += 1
        elif abs(signed_amt) >= 75000:
            row_status = "review"
            review_count += 1
        else:
            valid_count += 1

        transactions.append({
            "id": int(idx + 1),
            "transaction_date": d_str,
            "description": str(row.get("description", "Transaction")),
            "transaction_type": tx_type,
            "raw_amount": amt,
            "signed_amount": signed_amt,
            "counterparty": str(row.get("counterparty", "N/A")),
            "transaction_id": str(row.get("transaction_id", "") or "N/A"),
            "status": row_status
        })

    csv_content = "\n".join(csv_lines)

    return {
        "status": "success",
        "filename": pdf_file.filename,
        "row_count": len(transactions),
        "valid_count": valid_count,
        "review_count": review_count,
        "invalid_count": invalid_count,
        "coverage_months": res.get("coverage_months", 1.0),
        "date_start": res.get("date_start", ""),
        "date_end": res.get("date_end", ""),
        "warnings": res.get("warnings", []),
        "transactions": transactions,
        "csv_content": csv_content
    }

@router.post("", response_model=AnalysisRunResponse)
async def run_analysis(
    application_id: str = Form(...),
    transactions_file: UploadFile = File(...),
    utility_file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user)
):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, borrower_id, requested_amount, status FROM applications WHERE id = ?", (application_id,))
        app_row = cursor.fetchone()
        if not app_row:
            raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
            
        app_dict = dict(app_row)
        if current_user["role"] == "borrower" and app_dict["borrower_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Permission denied: Cannot submit analysis for another borrower's record")

    # Read transaction file content (Supports CSV and PDF bank statements)
    tx_content = await transactions_file.read()
    filename_lower = (transactions_file.filename or "").lower()

    if filename_lower.endswith(".pdf"):
        tx_res = parse_pdf_bank_statement(tx_content, transactions_file.filename)
    else:
        tx_res = parse_transaction_csv(tx_content, transactions_file.filename)

    if tx_res["status"] == "invalid":
        raise HTTPException(status_code=400, detail=tx_res["error_message"])

        
    punctuality_rate = 0.85
    utility_file_id = None
    if utility_file and utility_file.filename:
        ut_content = await utility_file.read()
        ut_res = parse_utility_csv(ut_content, utility_file.filename)
        if ut_res["status"] == "valid":
            punctuality_rate = ut_res["punctuality_rate"]

    # Compute cashflow features
    try:
        features = compute_cashflow_features(tx_res["dataframe"], punctuality_rate=punctuality_rate)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cash flow calculation error: {str(e)}")

    features["requested_amount"] = app_dict["requested_amount"]
    
    # Fraud & Integrity heuristics
    fraud_flags, fraud_risk_level = evaluate_fraud_heuristics(features, duplicate_count=tx_res["duplicate_count"])
    
    # ML Prediction
    pred = ml_engine.predict(features, data_confidence=tx_res["quality_level"])
    
    # Genuine SHAP Explanations
    explanations = shap_explainer.explain(features)
    
    # Loan Policy Recommendation
    policy_res = evaluate_loan_policy(
        score=pred["score"],
        lean_month_cash_flow=features["lean_month_cash_flow"],
        requested_amount=app_dict["requested_amount"],
        data_confidence=tx_res["quality_level"],
        fraud_risk_level=fraud_risk_level
    )
    
    # Counterfactual recommendations
    counterfactuals = [
        {
            "feature_name": "utility_payment_punctuality",
            "current_value": features["utility_payment_punctuality"],
            "target_value": 0.95,
            "scenario_assumptions": "Maintaining 95%+ on-time utility bill payments over the next 6 months",
            "plausibility_note": "Actionable positive credit behavior"
        },
        {
            "feature_name": "stable_monthly_cash_flow",
            "current_value": features["stable_monthly_cash_flow"],
            "target_value": round(features["stable_monthly_cash_flow"] * 1.2, -2),
            "scenario_assumptions": "20% sustained growth in monthly net business cash flow",
            "plausibility_note": "Business expansion scenario"
        }
    ]

    run_id = f"run_{uuid.uuid4().hex[:12]}"
    tx_file_id = f"file_{uuid.uuid4().hex[:12]}"

    full_response = {
        "analysis_run_id": run_id,
        "application_id": application_id,
        "model_version": MODEL_VERSION,
        "data": {
            "coverage_months": int(round(tx_res["coverage_months"])),
            "missing_months": 0,
            "data_confidence": tx_res["quality_level"],
            "warnings": tx_res["warnings"]
        },
        "cashflow": {
            "gross_business_inflow_monthly": features["gross_business_inflow_monthly"],
            "estimated_business_outflow_monthly": features["estimated_business_outflow_monthly"],
            "estimated_net_business_cash_flow": features["estimated_net_business_cash_flow"],
            "stable_monthly_cash_flow": features["stable_monthly_cash_flow"],
            "lean_month_cash_flow": features["lean_month_cash_flow"],
            "income_volatility": features["income_volatility"],
            "activity_regularity": features["activity_regularity"],
            "units": "INR",
            "classification_limitations": ["Categorization based on keyword heuristics and transaction amounts."]
        },
        "prediction": pred,
        "loan_policy": policy_res,
        "explanations": explanations,
        "counterfactuals": counterfactuals,
        "fraud_flags": fraud_flags,
        "disclaimers": [
            "Model trained on synthetic data for demonstration.",
            "All generated credit outcomes, risk probabilities, and policy recommendations are illustrative."
        ]
    }

    # Save to Database
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Save uploaded file record
        cursor.execute("""
            INSERT INTO uploaded_files (id, application_id, uploader_id, filename, file_type, checksum, row_count, date_start, date_end, validation_summary, status)
            VALUES (?, ?, ?, ?, 'transactions', ?, ?, ?, ?, ?, ?)
        """, (
            tx_file_id, application_id, current_user["id"], transactions_file.filename,
            tx_res["checksum"], tx_res["row_count"], tx_res["date_start"], tx_res["date_end"],
            json.dumps({"quality_level": tx_res["quality_level"], "warnings": tx_res["warnings"]}),
            tx_res["status"]
        ))
        
        # 2. Save Analysis Run
        cursor.execute("""
            INSERT INTO analysis_runs (
                id, application_id, uploaded_file_ids, feature_schema_version, model_version,
                score, score_range_low, score_range_high, score_range_type, default_probability,
                data_confidence, output_metadata
            ) VALUES (?, ?, ?, 1, ?, ?, ?, ?, 'heuristic', ?, ?, ?)
        """, (
            run_id, application_id, json.dumps([tx_file_id]), MODEL_VERSION,
            pred["score"], pred["score_range"]["low"], pred["score_range"]["high"],
            pred["default_probability"], tx_res["quality_level"], json.dumps(full_response)
        ))
        
        # 3. Save Score Explanations
        for exp in explanations:
            cursor.execute("""
                INSERT INTO score_explanations (id, analysis_run_id, feature_name, feature_value, contribution, output_space, direction, technical_text, borrower_text)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"exp_{uuid.uuid4().hex[:12]}", run_id, exp["feature_name"], exp["feature_value"], exp["contribution"],
                exp["output_space"], exp["direction"], exp["technical_text"], exp["borrower_text"]
            ))
            
        # 4. Save Counterfactuals
        for cf in counterfactuals:
            cursor.execute("""
                INSERT INTO counterfactuals (id, analysis_run_id, feature_name, current_value, target_value, scenario_assumptions, plausibility_note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                f"cf_{uuid.uuid4().hex[:12]}", run_id, cf["feature_name"], cf["current_value"], cf["target_value"],
                cf["scenario_assumptions"], cf["plausibility_note"]
            ))
            
        # 5. Save Fraud Flags
        for ff in fraud_flags:
            cursor.execute("""
                INSERT INTO fraud_flags (id, analysis_run_id, flag_type, severity, evidence_summary)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"ff_{uuid.uuid4().hex[:12]}", run_id, ff["flag_type"], ff["severity"], ff["evidence_summary"]
            ))
            
        # 6. Update Application status to Under Review
        if app_dict["status"] == "Submitted":
            cursor.execute("UPDATE applications SET status = 'Under Review', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (application_id,))
            
        # 7. Audit log
        cursor.execute("""
            INSERT INTO audit_logs (id, actor_id, actor_role, application_id, analysis_run_id, event_type, new_values, reason)
            VALUES (?, ?, ?, ?, ?, 'ANALYSIS_RUN', ?, 'Completed transaction data analysis and ML credit scoring run')
        """, (f"aud_{uuid.uuid4().hex[:12]}", current_user["id"], current_user["role"], application_id, run_id, json.dumps({"score": pred["score"], "prob": pred["default_probability"]})))

    return full_response

@router.get("/{run_id}", response_model=AnalysisRunResponse)
def get_analysis_run(run_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT output_metadata FROM analysis_runs WHERE id = ?", (run_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Analysis run not found")
            
        res = json.loads(row["output_metadata"])
        return res

@router.get("/{run_id}/explanation")
def get_analysis_explanation(run_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT feature_name, feature_value, contribution, direction, technical_text, borrower_text FROM score_explanations WHERE analysis_run_id = ?", (run_id,))
        rows = cursor.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Explanations not found for analysis run")
        return [dict(r) for r in rows]

@router.get("/{run_id}/counterfactuals")
def get_analysis_counterfactuals(run_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT feature_name, current_value, target_value, scenario_assumptions, plausibility_note FROM counterfactuals WHERE analysis_run_id = ?", (run_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]

@router.post("/whatif", response_model=WhatIfResponse)
def run_whatif(req: WhatIfRequest, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT output_metadata, data_confidence FROM analysis_runs WHERE id = ?", (req.analysis_run_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Analysis run not found for what-if simulation")
            
        ar_data = json.loads(row["output_metadata"])
        data_confidence = row["data_confidence"]
        
    cashflow = ar_data["cashflow"]
    prediction = ar_data["prediction"]
    loan_policy = ar_data["loan_policy"]
    
    # Reconstruct original feature map
    original_features = {
        "stable_monthly_cash_flow": cashflow["stable_monthly_cash_flow"],
        "lean_month_cash_flow": cashflow["lean_month_cash_flow"],
        "income_volatility": cashflow["income_volatility"],
        "activity_regularity": cashflow["activity_regularity"],
        "counterparty_concentration": 0.25,
        "utility_payment_punctuality": 0.85,
        "month_end_buffer": 1.0,
        "history_months": cashflow.get("coverage_months", 12),
        "seasonality_index": 1.2,
        "recent_inflow_spike_ratio": 1.0,
        "round_number_ratio": 0.2,
        "requested_amount": loan_policy["requested_amount"],
        "gross_business_inflow_monthly": cashflow["gross_business_inflow_monthly"]
    }
    
    overrides = {
        "analysis_run_id": req.analysis_run_id,
        "stable_cash_flow": req.stable_cash_flow,
        "utility_punctuality": req.utility_punctuality,
        "month_end_buffer": req.month_end_buffer,
        "requested_amount": req.requested_amount
    }
    
    res = simulate_whatif_scenario(
        original_features=original_features,
        original_score=prediction["score"],
        original_prob=prediction["default_probability"],
        original_recommended_amount=loan_policy["recommended_amount"],
        data_confidence=data_confidence,
        overrides=overrides
    )
    return res

@router.get("/{run_id}/report")
def download_assessment_report(run_id: str, current_user: dict = Depends(get_current_user)):
    """
    Generates and returns a downloadable PDF Credit Assessment & SHAP Explanation Report.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ar.output_metadata, u.full_name as borrower_name, app.id as app_id
            FROM analysis_runs ar
            JOIN applications app ON ar.application_id = app.id
            JOIN users u ON app.borrower_id = u.id
            WHERE ar.id = ?
        """, (run_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Analysis run not found")

        ar_data = json.loads(row["output_metadata"])
        borrower_name = row["borrower_name"]
        app_id = row["app_id"]

    try:
        pdf_bytes = generate_credit_assessment_pdf(
            analysis_data=ar_data,
            borrower_name=borrower_name,
            application_id=app_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF assessment report: {str(e)}")

    headers = {
        "Content-Disposition": f'attachment; filename="Credence_AI_Assessment_{app_id}.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


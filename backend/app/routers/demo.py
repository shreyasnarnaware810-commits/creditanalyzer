import os
import uuid
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.database import get_db
from app.auth.security import hash_password
from app.services.data_ingestion import parse_transaction_csv, parse_utility_csv
from app.services.cashflow_synthesizer import compute_cashflow_features
from app.services.fraud_heuristics import evaluate_fraud_heuristics
from app.services.ml_engine import ml_engine, MODEL_VERSION
from app.services.shap_explainer import shap_explainer
from app.services.loan_policy import evaluate_loan_policy

router = APIRouter(prefix="/api/demo", tags=["Demo"])

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sample_data")

@router.post("/seed")
def seed_demo_data():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Create Demo Officer Account if not existing
        cursor.execute("SELECT id FROM users WHERE username = 'officer_demo'")
        off_row = cursor.fetchone()
        if not off_row:
            officer_id = "usr_officer_demo_01"
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, role, full_name, is_demo_user)
                VALUES (?, 'officer_demo', 'officer@credence.ai', ?, 'officer', 'Sarah Jenkins (Loan Officer)', 1)
            """, (officer_id, hash_password("password123")))
        else:
            officer_id = off_row["id"]
            
        # 2. Create Demo Borrower (Meena) if not existing
        cursor.execute("SELECT id FROM users WHERE username = 'meena_demo'")
        meena_row = cursor.fetchone()
        if not meena_row:
            meena_id = "usr_meena_demo_01"
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, role, full_name, is_demo_user)
                VALUES (?, 'meena_demo', 'meena@synthetic-vendor.ai', ?, 'borrower', 'Meena (Vegetable Vendor - Synthetic)', 1)
            """, (meena_id, hash_password("password123")))
        else:
            meena_id = meena_row["id"]

        # 3. Create Preloaded Application for Meena
        cursor.execute("SELECT id FROM applications WHERE borrower_id = ?", (meena_id,))
        app_row = cursor.fetchone()
        if not app_row:
            app_id = "app_meena_demo_01"
            cursor.execute("""
                INSERT INTO applications (id, borrower_id, requested_amount, status, assigned_officer_id)
                VALUES (?, ?, 60000.0, 'Under Review', ?)
            """, (app_id, meena_id, officer_id))
            
            cursor.execute("""
                INSERT INTO consent_records (id, borrower_id, application_id, consent_version, purpose)
                VALUES (?, ?, ?, 'v1.0', 'Synthetic Alternative Scoring Assessment')
            """, (f"cns_{uuid.uuid4().hex[:12]}", meena_id, app_id))
        else:
            app_id = app_row["id"]

        # 4. Check if Analysis Run exists for Meena
        cursor.execute("SELECT id, output_metadata FROM analysis_runs WHERE application_id = ? ORDER BY created_at DESC LIMIT 1", (app_id,))
        ar_row = cursor.fetchone()
        
        if not ar_row:
            tx_path = os.path.join(SAMPLE_DIR, "meena_transactions.csv")
            ut_path = os.path.join(SAMPLE_DIR, "meena_utility.csv")
            
            with open(tx_path, "rb") as f:
                tx_content = f.read()
            with open(ut_path, "rb") as f:
                ut_content = f.read()
                
            tx_res = parse_transaction_csv(tx_content, "meena_transactions.csv")
            ut_res = parse_utility_csv(ut_content, "meena_utility.csv")
            
            features = compute_cashflow_features(tx_res["dataframe"], punctuality_rate=ut_res["punctuality_rate"])
            features["requested_amount"] = 60000.0
            
            fraud_flags, fraud_risk_level = evaluate_fraud_heuristics(features, duplicate_count=tx_res["duplicate_count"])
            pred = ml_engine.predict(features, data_confidence=tx_res["quality_level"])
            explanations = shap_explainer.explain(features)
            policy_res = evaluate_loan_policy(
                score=pred["score"],
                lean_month_cash_flow=features["lean_month_cash_flow"],
                requested_amount=60000.0,
                data_confidence=tx_res["quality_level"],
                fraud_risk_level=fraud_risk_level
            )
            
            counterfactuals = [
                {
                    "feature_name": "utility_payment_punctuality",
                    "current_value": features["utility_payment_punctuality"],
                    "target_value": 0.98,
                    "scenario_assumptions": "Sustained 98%+ punctuality over next 6 months",
                    "plausibility_note": "Highly achievable through automated reminders"
                },
                {
                    "feature_name": "stable_monthly_cash_flow",
                    "current_value": features["stable_monthly_cash_flow"],
                    "target_value": round(features["stable_monthly_cash_flow"] * 1.25, -2),
                    "scenario_assumptions": "25% expansion in vegetable wholesale sales",
                    "plausibility_note": "Seasonal festival expansion scenario"
                }
            ]

            run_id = "run_meena_demo_01"
            tx_file_id = "file_meena_tx_01"

            full_response = {
                "analysis_run_id": run_id,
                "application_id": app_id,
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

            cursor.execute("""
                INSERT INTO uploaded_files (id, application_id, uploader_id, filename, file_type, checksum, row_count, date_start, date_end, validation_summary, status)
                VALUES (?, ?, ?, 'meena_transactions.csv', 'transactions', ?, ?, ?, ?, ?, ?)
            """, (
                tx_file_id, app_id, meena_id, tx_res["checksum"], tx_res["row_count"],
                tx_res["date_start"], tx_res["date_end"], json.dumps({"quality_level": tx_res["quality_level"]}), "valid"
            ))

            cursor.execute("""
                INSERT INTO analysis_runs (
                    id, application_id, uploaded_file_ids, feature_schema_version, model_version,
                    score, score_range_low, score_range_high, score_range_type, default_probability,
                    data_confidence, output_metadata
                ) VALUES (?, ?, ?, 1, ?, ?, ?, ?, 'heuristic', ?, ?, ?)
            """, (
                run_id, app_id, json.dumps([tx_file_id]), MODEL_VERSION,
                pred["score"], pred["score_range"]["low"], pred["score_range"]["high"],
                pred["default_probability"], tx_res["quality_level"], json.dumps(full_response)
            ))

            for exp in explanations:
                cursor.execute("""
                    INSERT INTO score_explanations (id, analysis_run_id, feature_name, feature_value, contribution, output_space, direction, technical_text, borrower_text)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"exp_{uuid.uuid4().hex[:12]}", run_id, exp["feature_name"], exp["feature_value"], exp["contribution"],
                    exp["output_space"], exp["direction"], exp["technical_text"], exp["borrower_text"]
                ))

            for cf in counterfactuals:
                cursor.execute("""
                    INSERT INTO counterfactuals (id, analysis_run_id, feature_name, current_value, target_value, scenario_assumptions, plausibility_note)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"cf_{uuid.uuid4().hex[:12]}", run_id, cf["feature_name"], cf["current_value"], cf["target_value"],
                    cf["scenario_assumptions"], cf["plausibility_note"]
                ))

            cursor.execute("""
                INSERT INTO audit_logs (id, actor_id, actor_role, application_id, analysis_run_id, event_type, new_values, reason)
                VALUES (?, ?, 'borrower', ?, ?, 'SEED_DEMO', ?, 'Initialized preloaded synthetic demo application')
            """, (f"aud_{uuid.uuid4().hex[:12]}", meena_id, app_id, run_id, json.dumps({"score": pred["score"]})))
            
            analysis_data = full_response
        else:
            analysis_data = json.loads(ar_row["output_metadata"])

    return {
        "message": "Demo data successfully seeded",
        "demo_accounts": {
            "officer": {"username": "officer_demo", "password": "password123", "role": "officer"},
            "borrower": {"username": "meena_demo", "password": "password123", "role": "borrower"}
        },
        "application_id": app_id,
        "analysis_run_id": analysis_data["analysis_run_id"],
        "score": analysis_data["prediction"]["score"],
        "default_probability": analysis_data["prediction"]["default_probability"]
    }

@router.get("/sample-csv/{filename}")
def get_sample_csv(filename: str):
    allowed_files = ["meena_transactions.csv", "meena_utility.csv", "high_risk_transactions.csv", "fraud_flagged_transactions.csv"]
    if filename not in allowed_files:
        raise HTTPException(status_code=404, detail="File not found")
        
    filepath = os.path.join(SAMPLE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Sample CSV not generated yet")
        
    return FileResponse(filepath, media_type="text/csv", filename=filename)

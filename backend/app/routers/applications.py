import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schema import ApplicationCreateRequest, ApplicationResponse, OfficerDecisionRequest
from app.auth.security import get_current_user, require_officer
from app.database import get_db

router = APIRouter(prefix="/api/applications", tags=["Applications"])

@router.post("", response_model=ApplicationResponse)
def create_application(req: ApplicationCreateRequest, current_user: dict = Depends(get_current_user)):
    app_id = f"app_{uuid.uuid4().hex[:12]}"
    consent_id = f"cns_{uuid.uuid4().hex[:12]}"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO applications (id, borrower_id, requested_amount, status)
            VALUES (?, ?, ?, 'Submitted')
        """, (app_id, current_user["id"], req.requested_amount))
        
        cursor.execute("""
            INSERT INTO consent_records (id, borrower_id, application_id, consent_version, purpose)
            VALUES (?, ?, ?, ?, ?)
        """, (consent_id, current_user["id"], app_id, req.consent_version, "Alternative Credit Scoring & Cashflow Assessment"))
        
        cursor.execute("""
            INSERT INTO audit_logs (id, actor_id, actor_role, application_id, event_type, new_values, reason)
            VALUES (?, ?, ?, ?, 'APPLICATION_CREATED', ?, 'Borrower created new loan application')
        """, (f"aud_{uuid.uuid4().hex[:12]}", current_user["id"], current_user["role"], app_id, json.dumps({"requested_amount": req.requested_amount})))

        cursor.execute("SELECT id, borrower_id, requested_amount, status, assigned_officer_id, created_at, updated_at FROM applications WHERE id = ?", (app_id,))
        app_row = dict(cursor.fetchone())
        app_row["borrower_name"] = current_user["full_name"]
        return app_row

@router.get("", response_model=List[ApplicationResponse])
def list_applications(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        if current_user["role"] == "officer":
            cursor.execute("""
                SELECT a.id, a.borrower_id, a.requested_amount, a.status, a.assigned_officer_id, a.created_at, a.updated_at,
                       u.full_name as borrower_name,
                       ar.id as latest_analysis_run_id, ar.score, ar.default_probability, ar.data_confidence
                FROM applications a
                JOIN users u ON a.borrower_id = u.id
                LEFT JOIN analysis_runs ar ON ar.application_id = a.id
                GROUP BY a.id
                ORDER BY a.created_at DESC
            """)
        else:
            cursor.execute("""
                SELECT a.id, a.borrower_id, a.requested_amount, a.status, a.assigned_officer_id, a.created_at, a.updated_at,
                       u.full_name as borrower_name,
                       ar.id as latest_analysis_run_id, ar.score, ar.default_probability, ar.data_confidence
                FROM applications a
                JOIN users u ON a.borrower_id = u.id
                LEFT JOIN analysis_runs ar ON ar.application_id = a.id
                WHERE a.borrower_id = ?
                GROUP BY a.id
                ORDER BY a.created_at DESC
            """, (current_user["id"],))
            
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            result.append(d)
        return result

@router.get("/{id}", response_model=ApplicationResponse)
def get_application(id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.borrower_id, a.requested_amount, a.status, a.assigned_officer_id, a.created_at, a.updated_at,
                   u.full_name as borrower_name,
                   ar.id as latest_analysis_run_id, ar.score, ar.default_probability, ar.data_confidence
            FROM applications a
            JOIN users u ON a.borrower_id = u.id
            LEFT JOIN analysis_runs ar ON ar.application_id = a.id
            WHERE a.id = ?
            ORDER BY ar.created_at DESC LIMIT 1
        """, (id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Application not found")
        
        app_dict = dict(row)
        # Server-side authorization check: borrower can only view own application
        if current_user["role"] == "borrower" and app_dict["borrower_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Permission denied: Cannot access another borrower's record")
            
        return app_dict

@router.post("/{id}/decision")
def record_decision(id: str, req: OfficerDecisionRequest, current_user: dict = Depends(require_officer)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, status, requested_amount FROM applications WHERE id = ?", (id,))
        app_row = cursor.fetchone()
        if not app_row:
            raise HTTPException(status_code=404, detail="Application not found")
            
        old_status = app_row["status"]
        
        # Get latest analysis run to check policy recommendation
        cursor.execute("SELECT id, model_version, output_metadata FROM analysis_runs WHERE application_id = ? ORDER BY created_at DESC LIMIT 1", (id,))
        ar_row = cursor.fetchone()
        
        recommended_status = "Approved" if req.status == "Approved" else req.status
        recommended_amount = app_row["requested_amount"]
        ar_id = None
        
        if ar_row:
            ar_id = ar_row["id"]
            meta = json.loads(ar_row["output_metadata"])
            recommended_amount = meta.get("loan_policy", {}).get("recommended_amount", app_row["requested_amount"])
            recommended_status = meta.get("loan_policy", {}).get("recommendation_status", "Approved Suggested")
            if "Approved" in recommended_status:
                recommended_status = "Approved"
            elif "Decline" in recommended_status:
                recommended_status = "Declined"
            elif "More Info" in recommended_status:
                recommended_status = "More Info Required"

        # Mandatory override reason validation
        is_status_override = (req.status != recommended_status)
        is_amount_override = (req.approved_amount is not None and abs(req.approved_amount - recommended_amount) > 1.0)
        
        if (is_status_override or is_amount_override) and (not req.override_reason or len(req.override_reason.strip()) < 5):
            raise HTTPException(
                status_code=400,
                detail="Mandatory override reason is required whenever officer decision or amount differs from policy recommendation."
            )
            
        # Update application status
        cursor.execute("""
            UPDATE applications
            SET status = ?, assigned_officer_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (req.status, current_user["id"], id))
        
        # Record Audit Log
        audit_id = f"aud_{uuid.uuid4().hex[:12]}"
        new_vals = {
            "status": req.status,
            "approved_amount": req.approved_amount if req.approved_amount is not None else recommended_amount,
            "notes": req.notes
        }
        cursor.execute("""
            INSERT INTO audit_logs (id, actor_id, actor_role, application_id, analysis_run_id, event_type, old_values, new_values, reason)
            VALUES (?, ?, ?, ?, ?, 'OFFICER_DECISION', ?, ?, ?)
        """, (
            audit_id,
            current_user["id"],
            current_user["role"],
            id,
            ar_id,
            json.dumps({"status": old_status}),
            json.dumps(new_vals),
            req.override_reason or "Officer decision recorded without override"
        ))
        
        return {
            "message": f"Decision successfully recorded: {req.status}",
            "application_id": id,
            "status": req.status,
            "audit_id": audit_id
        }

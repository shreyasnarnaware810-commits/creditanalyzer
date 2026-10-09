import json
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from app.models.schema import AuditLogItem
from app.auth.security import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("/{application_id}", response_model=List[AuditLogItem])
def get_application_audit_history(application_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, borrower_id FROM applications WHERE id = ?", (application_id,))
        app_row = cursor.fetchone()
        if not app_row:
            raise HTTPException(status_code=404, detail="Application not found")
            
        # Access control check
        if current_user["role"] == "borrower" and app_row["borrower_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Permission denied: Cannot view audit trail for another borrower")

        cursor.execute("""
            SELECT a.id, a.actor_id, a.actor_role, a.application_id, a.analysis_run_id, a.event_type,
                   a.old_values, a.new_values, a.reason, a.timestamp,
                   u.full_name as actor_name
            FROM audit_logs a
            LEFT JOIN users u ON a.actor_id = u.id
            WHERE a.application_id = ?
            ORDER BY a.timestamp DESC
        """, (application_id,))
        
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if d["old_values"]:
                d["old_values"] = json.loads(d["old_values"])
            if d["new_values"]:
                d["new_values"] = json.loads(d["new_values"])
            result.append(d)
        return result

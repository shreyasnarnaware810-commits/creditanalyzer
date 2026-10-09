from fastapi import APIRouter, Depends
from app.models.schema import FairnessResponse
from app.auth.security import get_current_user
from app.services.fairness_monitor import compute_fairness_metrics

router = APIRouter(prefix="/api/fairness", tags=["Fairness"])

@router.get("", response_model=FairnessResponse)
def get_fairness_metrics(current_user: dict = Depends(get_current_user)):
    res = compute_fairness_metrics()
    return res

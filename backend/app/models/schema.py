from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any

# Auth Schemas
class UserSignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(...)
    password: str = Field(..., min_length=6)
    full_name: str = Field(...)
    role: str = Field("borrower", pattern="^(officer|borrower)$")

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    full_name: str
    is_demo_user: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Application Schemas
class ApplicationCreateRequest(BaseModel):
    requested_amount: float = Field(..., gt=0)
    consent_given: bool = Field(True)
    consent_version: str = Field("v1.0")

class ApplicationResponse(BaseModel):
    id: str
    borrower_id: str
    requested_amount: float
    status: str
    assigned_officer_id: Optional[str] = None
    created_at: str
    updated_at: str
    borrower_name: Optional[str] = None
    latest_analysis_run_id: Optional[str] = None
    score: Optional[int] = None
    default_probability: Optional[float] = None
    data_confidence: Optional[str] = None

# Analysis Schemas
class DataSummary(BaseModel):
    coverage_months: int
    missing_months: int
    data_confidence: str
    warnings: List[str]

class CashFlowSummary(BaseModel):
    gross_business_inflow_monthly: float
    estimated_business_outflow_monthly: float
    estimated_net_business_cash_flow: float
    stable_monthly_cash_flow: float
    lean_month_cash_flow: float
    income_volatility: float
    activity_regularity: float
    units: str = "INR"
    classification_limitations: List[str]

class ScoreRange(BaseModel):
    low: int
    high: int
    type: str = "heuristic"

class PredictionResult(BaseModel):
    score: int
    default_probability: float
    probability_label: str = "synthetic-model estimate"
    score_range: ScoreRange

class LoanPolicyResult(BaseModel):
    requested_amount: float
    recommended_amount: float
    policy_version: str = "demo_policy_v1"
    recommendation_status: str = "Recommended"
    limitations: List[str]

class ExplanationItem(BaseModel):
    feature_name: str
    feature_value: float
    contribution: float
    output_space: str = "score_points"
    direction: str
    technical_text: str
    borrower_text: str

class CounterfactualItem(BaseModel):
    feature_name: str
    current_value: float
    target_value: float
    scenario_assumptions: str
    plausibility_note: str

class FraudFlagItem(BaseModel):
    flag_type: str
    severity: str
    evidence_summary: str

class AnalysisRunResponse(BaseModel):
    analysis_run_id: str
    application_id: str
    model_version: str
    data: DataSummary
    cashflow: CashFlowSummary
    prediction: PredictionResult
    loan_policy: LoanPolicyResult
    explanations: List[ExplanationItem]
    counterfactuals: List[CounterfactualItem]
    fraud_flags: List[FraudFlagItem]
    disclaimers: List[str]

# What-If Request & Response
class WhatIfRequest(BaseModel):
    analysis_run_id: str
    stable_cash_flow: Optional[float] = None
    utility_punctuality: Optional[float] = Field(None, ge=0.0, le=1.0)
    month_end_buffer: Optional[float] = None
    requested_amount: Optional[float] = None

class WhatIfResponse(BaseModel):
    original_analysis_run_id: str
    hypothetical_score: int
    score_change: int
    hypothetical_default_probability: float
    probability_change: float
    original_recommended_amount: float
    hypothetical_recommended_amount: float
    changed_inputs: Dict[str, Any]
    disclaimer: str = "Hypothetical scenario under prototype model. This scenario does not guarantee loan eligibility or approval."

# Officer Decision Request
class OfficerDecisionRequest(BaseModel):
    status: str = Field(..., pattern="^(Approved|Declined|More Info Required)$")
    approved_amount: Optional[float] = None
    override_reason: Optional[str] = None
    notes: Optional[str] = None

# Audit Log Item
class AuditLogItem(BaseModel):
    id: str
    actor_id: str
    actor_role: str
    actor_name: Optional[str] = None
    application_id: str
    analysis_run_id: Optional[str] = None
    event_type: str
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    timestamp: str

# Fairness Metrics Schema
class GroupFairnessMetric(BaseModel):
    group_name: str
    sample_count: int
    approval_rate: float
    score_average: float
    auc: float
    disparate_impact_ratio: float

class FairnessResponse(BaseModel):
    model_version: str
    dataset_identifier: str
    groups: List[GroupFairnessMetric]
    overall_disparate_impact: float
    disclaimer: str = "No protected attributes are used as model inputs. Metrics shown here are measured on synthetic data and must be re-evaluated on representative, lawfully collected real data before any production use."

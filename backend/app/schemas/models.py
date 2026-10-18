"""
DESHMRITTIKA / BHUMI-SYNC — Pydantic Data Contracts & Schemas
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    role: str
    status: str = "ACTIVE"
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    confirm_password: str
    phone: Optional[str] = ""
    role: Optional[str] = "CITIZEN"
    terms_agreed: bool = True

class VerifyEmailRequest(BaseModel):
    email: str
    code: str

class ResendCodeRequest(BaseModel):
    email: str
    purpose: str = "EMAIL_VERIFY"

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str
    confirm_password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: str
    phone: Optional[str] = ""
    role: str
    status: str
    created_at: str

class AdminRoleChangeRequest(BaseModel):
    target_user_id: str
    new_role: str
    reason: str

class AdminStatusChangeRequest(BaseModel):
    target_user_id: str
    new_status: str
    reason: str

class ParcelSummary(BaseModel):
    parcel_id: str
    district: str
    upazila: str
    mouza: str
    jl_number: int
    dag_number: int
    khatian_number: int
    survey_type: str
    land_classification: str
    area_decimal: float
    is_disputed: bool
    provenance_label: str

class ParcelDetail(ParcelSummary):
    coordinates_geojson: Optional[str] = None
    current_owners: List[Dict[str, Any]] = []
    historical_deeds: List[Dict[str, Any]] = []
    mutations: List[Dict[str, Any]] = []
    tax_status: Optional[Dict[str, Any]] = None
    litigations: List[Dict[str, Any]] = []
    khas_status: Optional[Dict[str, Any]] = None
    verification_cases: List[Dict[str, Any]] = []

class SearchResult(BaseModel):
    total_matches: int
    parcels: List[ParcelSummary]

class VerificationFinding(BaseModel):
    finding_code: str
    severity: str
    risk_score: int
    explanation_bn: str
    explanation_en: str
    evidence_references: Dict[str, Any]
    recommendation: str

class ParcelEvaluationReport(BaseModel):
    parcel_id: str
    overall_risk_score: int
    overall_status: str
    findings: List[VerificationFinding]
    is_safe_for_transaction: bool
    disclaimer: str

class DueDiligenceDossier(BaseModel):
    parcel: ParcelSummary
    ownership_chain_verified: bool
    unmutated_deeds_count: int
    active_disputes_count: int
    tax_compliant: bool
    is_government_khas: bool
    is_acquisition_corridor: bool
    risk_score: int
    safety_rating: str  # SAFE, CAUTION, HIGH_RISK, CRITICAL_BLOCKED
    safety_checklist: List[Dict[str, Any]]
    findings: List[VerificationFinding]
    disclaimer: str

class MutationPreCheckRequest(BaseModel):
    parcel_id: str
    deed_id: str
    applicant_id: str

class MutationPreCheckResponse(BaseModel):
    can_proceed: bool
    tax_arrears: bool
    active_injunction: bool
    is_khas_land: bool
    competing_unmutated_deed: bool
    rejection_reasons: List[str]
    precheck_summary_bn: str

class DocumentVerifyRequest(BaseModel):
    document_id: Optional[str] = None
    sha256_hash: Optional[str] = None

class DocumentVerifyResponse(BaseModel):
    is_authentic: bool
    matched_document_id: Optional[str] = None
    parcel_id: Optional[str] = None
    deed_id: Optional[str] = None
    document_type: Optional[str] = None
    status_label: str
    provenance_label: str
    calculated_hash: Optional[str] = None
    reference_hash: Optional[str] = None
    comparison_status: Optional[str] = None

class ReviewDecisionRequest(BaseModel):
    case_id: str
    action: str  # APPROVED_LEGITIMATE, REJECTED_FRAUD_FLAG, REQUESTED_PHYSICAL_INSPECTION
    reason: str

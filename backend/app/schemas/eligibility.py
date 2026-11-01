from enum import Enum
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class EligibilityStatusEnum(str, Enum):
    POTENTIALLY_ELIGIBLE = "potentially_eligible"
    NOT_ELIGIBLE = "not_eligible"
    NEEDS_INFORMATION = "needs_information"
    NOT_ASSESSED = "not_assessed"


class EvaluatedRule(BaseModel):
    rule_key: str
    condition_description: str
    required: bool
    user_value: Optional[Any] = None
    expected_value: Any
    passed: Optional[bool] = None  # None indicates missing information
    source_section: Optional[str] = None


class EligibilityCheckRequest(BaseModel):
    # Optional override profile fields; if omitted, uses saved profile
    annual_family_income: Optional[float] = None
    caste_category: Optional[str] = None
    education_level: Optional[str] = None
    course: Optional[str] = None
    state_code: Optional[str] = None
    is_differently_abled: Optional[bool] = None
    gender: Optional[str] = None
    student_status: Optional[str] = "Student"


class EligibilityCheckResponse(BaseModel):
    scheme_id: str
    scheme_slug: str
    scheme_name: str
    status: EligibilityStatusEnum
    summary_explanation: str
    matched_rules: List[EvaluatedRule] = []
    failed_rules: List[EvaluatedRule] = []
    missing_fields: List[str] = []
    official_source_clause: Optional[str] = None
    disclaimer: str = "Informational assessment only based on official scheme guidelines. Not an official government decision."


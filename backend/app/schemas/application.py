from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ApplicationDraftCreate(BaseModel):
    scheme_id: str = Field(..., description="Target scheme slug or id")
    form_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Pre-filled citizen details")


class ApplicationDraftUpdate(BaseModel):
    form_data: Dict[str, Any]


class ApplicationDraftResponse(BaseModel):
    id: str
    user_id: str
    scheme_id: str
    scheme_name: str
    status: str
    form_data: Dict[str, Any]
    automation_log: Optional[List[str]] = None
    created_at: str
    updated_at: str


class DemoPrepareRequest(BaseModel):
    confirmed_by_user: bool = Field(..., description="Explicit citizen confirmation required before initiating demo")


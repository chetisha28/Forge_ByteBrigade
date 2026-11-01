from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class CitizenRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Citizen's full legal name")
    email_or_mobile: str = Field(..., min_length=5, max_length=100, description="Email address or 10-digit mobile number")
    state_code: Optional[str] = Field("Gujarat", description="State or UT of domicile")
    education_level: Optional[str] = Field("Undergraduate", description="Education level")
    password: str = Field(..., min_length=4, description="Citizen account password or access PIN")


class CitizenLoginRequest(BaseModel):
    email_or_mobile: str = Field(..., description="Registered email address or mobile number")
    password: str = Field(..., description="Access password or PIN")


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    full_name: str
    email_or_mobile: str
    state_code: Optional[str] = None
    is_demo_user: bool = False


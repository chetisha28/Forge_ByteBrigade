from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProfileBase(BaseModel):
    full_name: Optional[str] = Field(None, description="Full name of applicant")
    state_code: Optional[str] = Field(None, description="State of domicile (e.g. Gujarat, Maharashtra, Delhi)")
    education_level: Optional[str] = Field(None, description="Current education level (e.g. 10th Passed, 12th Passed, Undergraduate, Postgraduate)")
    course: Optional[str] = Field(None, description="Current course of study (e.g. B.Tech, B.Sc, MBBS, Class 11)")
    study_year: Optional[int] = Field(None, description="Current year of study (1, 2, 3, etc.)")
    institution_name: Optional[str] = Field(None, description="Name of educational institution")
    annual_family_income: Optional[float] = Field(None, description="Annual gross household income in INR")
    caste_category: Optional[str] = Field(None, description="Social category: General, SC, ST, OBC, EWS, Minority")
    gender: Optional[str] = Field(None, description="Gender (Female, Male, Other)")
    is_differently_abled: Optional[bool] = Field(False, description="Person with disability (PwD / UDID holder)")


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: str
    completeness_percentage: int = Field(0, description="Calculated profile completeness")

    model_config = ConfigDict(from_attributes=True)



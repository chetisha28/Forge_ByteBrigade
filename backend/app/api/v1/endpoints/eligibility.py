from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.eligibility import EligibilityCheckRequest, EligibilityCheckResponse
from backend.app.services.eligibility_engine import eligibility_engine
from backend.app.services.profile_service import profile_service

router = APIRouter(prefix="/schemes", tags=["Eligibility"])


@router.post("/{scheme_slug}/eligibility-check", response_model=EligibilityCheckResponse)
async def check_eligibility(scheme_slug: str, request: EligibilityCheckRequest):
    """
    Deterministic evaluation of citizen eligibility against official scheme conditions.
    Does not use non-deterministic LLM decisions; strictly evaluates rules, income ceilings,
    and category constraints.
    """
    # Merge saved profile with any client-provided overrides
    profile = profile_service.get_profile().model_dump()
    overrides = request.model_dump(exclude_unset=True)
    profile.update(overrides)

    result = eligibility_engine.evaluate(scheme_slug, profile)
    return result


from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.auth import CitizenRegisterRequest, CitizenLoginRequest, AuthTokenResponse
from backend.app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Citizen Authentication"])


@router.post("/register", response_model=AuthTokenResponse)
async def register_citizen(request: CitizenRegisterRequest):
    """Register a new citizen account with basic profile facts."""
    return auth_service.register(request)


@router.post("/login", response_model=AuthTokenResponse)
async def login_citizen(request: CitizenLoginRequest):
    """Authenticate citizen using registered email or mobile number."""
    token = auth_service.login(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your email/mobile or access PIN."
        )
    return token


@router.post("/demo-login", response_model=AuthTokenResponse)
async def login_demo_citizen():
    """Sign in as standard demo student persona (Aarav Sharma) for rapid demonstration."""
    return auth_service.get_demo_user()


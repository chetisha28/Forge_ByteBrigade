from fastapi import APIRouter
from backend.app.api.v1.endpoints import auth, profiles, schemes, eligibility, assistant, documents, applications

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(profiles.router)
api_router.include_router(schemes.router)
api_router.include_router(eligibility.router)
api_router.include_router(assistant.router)
api_router.include_router(documents.router)
api_router.include_router(applications.router)




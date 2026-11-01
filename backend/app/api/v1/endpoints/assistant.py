from fastapi import APIRouter
from backend.app.schemas.assistant import AssistantQueryRequest, AssistantQueryResponse
from backend.app.services.rag_service import rag_service

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/query", response_model=AssistantQueryResponse)
async def query_assistant(request: AssistantQueryRequest):
    """
    RAG-grounded question answering over official government scheme guidelines.
    Returns factual answers with verified citations and source URLs.
    Flags insufficient_evidence if official documents do not contain the answer.
    """
    return rag_service.answer_query(request)


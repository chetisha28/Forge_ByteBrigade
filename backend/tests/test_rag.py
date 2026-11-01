import pytest
from backend.app.services.rag_service import rag_service
from backend.app.schemas.assistant import AssistantQueryRequest


def test_rag_grounded_answer_with_citations():
    """Querying scholarship income limit returns cited official guidelines."""
    req = AssistantQueryRequest(
        scheme_id="national-scholarship-post-matric",
        question="What is the family income limit for the scholarship?"
    )
    resp = rag_service.answer_query(req)
    assert not resp.insufficient_evidence
    assert len(resp.citations) > 0
    assert "scholarship" in resp.citations[0].source_title.lower()
    assert "2,50,000" in resp.answer or "4,50,000" in resp.answer or "income" in resp.answer.lower()


def test_rag_insufficient_evidence_handling():
    """Unrelated or ungrounded questions safely return insufficient_evidence=True."""
    req = AssistantQueryRequest(
        scheme_id="national-scholarship-post-matric",
        question="What is the ticket price for Disneyland Paris in Euros?"
    )
    resp = rag_service.answer_query(req)
    assert resp.insufficient_evidence
    assert len(resp.citations) == 0


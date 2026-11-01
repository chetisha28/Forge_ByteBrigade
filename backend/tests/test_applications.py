import pytest
from backend.app.services.application_service import application_service
from backend.app.schemas.application import ApplicationDraftCreate


def test_application_draft_and_controlled_demo():
    """Application draft populates profile facts and demo enforces stop-before-submit."""
    draft = application_service.create_draft(ApplicationDraftCreate(
        scheme_id="national-scholarship-post-matric",
        form_data={"course_name": "B.Tech Computer Science"}
    ))
    assert draft.status == "ready_for_review"
    assert "Aarav" in draft.form_data["applicant_name"]

    # Run controlled demo
    demo_resp = application_service.prepare_demo(draft.id)
    assert demo_resp.status == "demo_completed"
    assert any("SAFETY GUARDRAIL" in log for log in demo_resp.automation_log)


import pytest
from backend.app.services.document_service import document_service


def test_document_extraction_and_confirmation():
    """Document parsing requires human confirmation before status becomes verified."""
    upload_resp = document_service.simulate_or_parse_upload(
        "Income_Certificate_Tehsildar.pdf", b"%PDF-1.4 sample content"
    )
    assert upload_resp.processing_status == "awaiting_user_confirmation"
    assert upload_resp.extracted_fields is not None

    # Confirm extraction
    confirmed = document_service.confirm_extraction(upload_resp.id, {"annual_family_income": 220000.0})
    assert confirmed.processing_status == "verified"
    assert confirmed.user_confirmed_fields["annual_family_income"] == 220000.0


import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_auth_demo_login():
    resp = client.post("/api/v1/auth/demo-login")
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Aarav Sharma"
    assert "access_token" in data


def test_auth_register_and_login():
    reg_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Priya Patel",
        "email_or_mobile": "priya.patel@test.in",
        "state_code": "Gujarat",
        "password": "securepassword123"
    })
    assert reg_resp.status_code == 200
    assert reg_resp.json()["full_name"] == "Priya Patel"

    login_resp = client.post("/api/v1/auth/login", json={
        "email_or_mobile": "priya.patel@test.in",
        "password": "securepassword123"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["full_name"] == "Priya Patel"


def test_schemes_list_endpoint():
    # Scholarship filter returns >500 schemes
    resp = client.get("/api/v1/schemes?scheme_type=scholarship&page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 500
    assert len(data["items"]) == 5

    # All schemes query returns >2000 schemes
    resp_all = client.get("/api/v1/schemes?scheme_type=&page=1&page_size=5")
    assert resp_all.status_code == 200
    assert resp_all.json()["total"] > 2000



def test_scheme_detail_endpoint():
    resp = client.get("/api/v1/schemes/national-scholarship-post-matric")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "national-scholarship-post-matric"
    assert len(data["detected_document_tags"]) > 0


def test_eligibility_check_endpoint():
    resp = client.post(
        "/api/v1/schemes/national-scholarship-post-matric/eligibility-check",
        json={"annual_family_income": 200000.0, "caste_category": "OBC"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "potentially_eligible"


def test_assistant_query_endpoint():
    resp = client.post(
        "/api/v1/assistant/query",
        json={
            "scheme_id": "national-scholarship-post-matric",
            "question": "What is the family income limit for this scholarship?"
        }
    )
    assert resp.status_code == 200
    data = resp.json()
    assert not data["insufficient_evidence"]
    assert len(data["citations"]) > 0


def test_documents_list_endpoint():
    resp = client.get("/api/v1/documents")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


def test_applications_drafts_endpoint():
    resp = client.get("/api/v1/applications/drafts")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


def test_registered_user_isolation():
    """Verify newly registered citizen has an unseeded profile, 0 documents, and 0 drafts."""
    reg_resp = client.post("/api/v1/auth/register", json={
        "full_name": "Rohan Deshmukh",
        "email_or_mobile": "rohan.deshmukh@test.in",
        "state_code": "Maharashtra",
        "password": "mypassword123"
    })
    assert reg_resp.status_code == 200
    user_data = reg_resp.json()
    token = user_data["access_token"]
    user_id = user_data["user_id"]
    headers = {"Authorization": f"Bearer {token}", "X-User-ID": user_id}

    # Profile must belong to Rohan, not Aarav Sharma
    prof_resp = client.get("/api/v1/profiles/me", headers=headers)
    assert prof_resp.status_code == 200
    prof = prof_resp.json()
    assert prof["full_name"] == "Rohan Deshmukh"
    assert prof["state_code"] == "Maharashtra"
    assert prof["annual_family_income"] is None
    assert prof["course"] is None

    # Documents must be empty (clean vault)
    docs_resp = client.get("/api/v1/documents", headers=headers)
    assert docs_resp.status_code == 200
    assert len(docs_resp.json()) == 0

    # Drafts must be empty
    drafts_resp = client.get("/api/v1/applications/drafts", headers=headers)
    assert drafts_resp.status_code == 200
    assert len(drafts_resp.json()) == 0

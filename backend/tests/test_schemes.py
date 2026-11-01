import pytest
from backend.app.services.scheme_service import scheme_service
from backend.app.schemas.scheme import SchemeRecommendationRequest


def test_scheme_catalog_loaded():
    """Verify authentic dataset loaded correctly."""
    assert len(scheme_service._schemes) > 2000
    res = scheme_service.list_schemes(page=1, page_size=10)
    assert res.total > 2000
    assert len(res.items) == 10


def test_scheme_search_query():
    """Searching for 'scholarship' yields relevant schemes."""
    res = scheme_service.list_schemes(q="scholarship", page_size=5)
    assert res.total > 0
    for item in res.items:
        scheme_full = scheme_service.get_scheme_by_slug(item.slug)
        text = f"{scheme_full.name} {scheme_full.description} {scheme_full.benefit_summary}".lower()
        assert "scholarship" in text or "student" in text or "fellowship" in text or "education" in text



def test_scheme_recommendations():
    """Recommendations return structured match reasons based on student profile."""
    req = SchemeRecommendationRequest(
        state_code="Gujarat",
        education_level="Undergraduate",
        caste_category="OBC",
        annual_family_income=200000.0,
        gender="Male",
        limit=5
    )
    recs = scheme_service.get_recommendations(req)
    assert len(recs) > 0
    for r in recs:
        assert r.recommendation_reason is not None
        assert len(r.recommendation_reason) > 5


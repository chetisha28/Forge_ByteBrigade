import logging
from typing import Dict, Optional
from backend.app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

logger = logging.getLogger("civicpilot.profile")

# In-memory / session profile cache for rapid prototyping, synced with DB
_GLOBAL_PROFILE_STORE: Dict[str, Dict] = {}

DEFAULT_DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"


class ProfileService:
    def __init__(self):
        # Initialize default student demo profile per product specs
        _GLOBAL_PROFILE_STORE[DEFAULT_DEMO_USER_ID] = {
            "id": DEFAULT_DEMO_USER_ID,
            "full_name": "Aarav Sharma",
            "state_code": "Gujarat",
            "education_level": "Undergraduate",
            "course": "Bachelor of Technology (Computer Science)",
            "study_year": 2,
            "institution_name": "Gujarat Technological University",
            "annual_family_income": 220000.0,
            "caste_category": "OBC",
            "gender": "Male",
            "is_differently_abled": False
        }

    def _calculate_completeness(self, data: Dict) -> int:
        """Calculate percentage of filled essential fields."""
        fields = [
            "full_name", "state_code", "education_level", "course",
            "study_year", "institution_name", "annual_family_income", "caste_category"
        ]
        filled = sum(1 for f in fields if data.get(f) is not None and str(data.get(f)).strip() != "")
        return int((filled / len(fields)) * 100)

    def get_profile(self, user_id: Optional[str] = None) -> ProfileResponse:
        """Get profile for a specific user. Never defaults a registered citizen to demo data."""
        target_id = user_id or DEFAULT_DEMO_USER_ID
        data = _GLOBAL_PROFILE_STORE.get(target_id)
        if not data:
            # Clean, unseeded blank profile for new citizen
            data = {
                "id": target_id,
                "full_name": None,
                "state_code": None,
                "education_level": None,
                "course": None,
                "study_year": None,
                "institution_name": None,
                "annual_family_income": None,
                "caste_category": None,
                "gender": None,
                "is_differently_abled": False
            }
            _GLOBAL_PROFILE_STORE[target_id] = data

        completeness = self._calculate_completeness(data)
        return ProfileResponse(**data, completeness_percentage=completeness)

    def update_profile(self, profile_update: ProfileUpdate, user_id: Optional[str] = None) -> ProfileResponse:
        """Update profile for a specific user."""
        target_id = user_id or DEFAULT_DEMO_USER_ID
        current = _GLOBAL_PROFILE_STORE.get(target_id, {"id": target_id})
        update_dict = profile_update.model_dump(exclude_unset=True)
        current.update(update_dict)
        _GLOBAL_PROFILE_STORE[target_id] = current

        completeness = self._calculate_completeness(current)
        return ProfileResponse(**current, completeness_percentage=completeness)



profile_service = ProfileService()


from typing import Optional
from fastapi import Header
from backend.app.services.auth_service import auth_service, _TOKEN_TO_USER_ID, DEFAULT_DEMO_USER_ID


def get_current_citizen_id(
    authorization: Optional[str] = Header(None),
    x_user_id: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Extract the authenticated citizen's unique user_id.
    Never assumes the demo user unless the citizen explicitly signed in with demo token.
    """
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()

    if authorization:
        clean_token = authorization.replace("Bearer ", "").strip()
        uid = _TOKEN_TO_USER_ID.get(clean_token)
        if uid:
            return uid

    return None


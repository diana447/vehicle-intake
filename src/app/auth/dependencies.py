import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.schemas import CurrentUser
from app.common.exceptions import AuthenticationError
from app.common.messages import INVALID_AUTH_MESSAGE, NOT_AUTHENTICATED_MESSAGE
from app.organizations.models.organization import Organization
from config.settings import get_settings

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    if credentials is None:
        raise AuthenticationError(detail=NOT_AUTHENTICATED_MESSAGE)
    try:
        payload = jwt.decode(
            credentials.credentials,
            get_settings().JWT_SECRET,
            algorithms=["HS256"],
            options={"require": ["exp", "sub", "org_id", "org_type"]},
        )
        return CurrentUser(
            sub=payload["sub"],
            org_id=payload["org_id"],
            org_type=Organization.Type(payload["org_type"].upper()),
        )
    except (jwt.PyJWTError, ValueError):
        raise AuthenticationError(detail=INVALID_AUTH_MESSAGE)

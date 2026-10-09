"""JWT creation/verification. Auth flow itself lives in services/auth_service."""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import AuthError

ALGORITHM = "HS256"


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {"sub": subject, "type": token_type, "iat": now, "exp": now + expires_delta}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def create_access_token(user_id: str) -> str:
    s = get_settings()
    return _create_token(user_id, "access", timedelta(minutes=s.access_token_expire_minutes))


def create_refresh_token(user_id: str) -> str:
    s = get_settings()
    return _create_token(user_id, "refresh", timedelta(days=s.refresh_token_expire_days))


def decode_token(token: str, expected_type: str = "access") -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise AuthError("Invalid or expired token") from exc
    if payload.get("type") != expected_type:
        raise AuthError("Wrong token type")
    return str(payload["sub"])

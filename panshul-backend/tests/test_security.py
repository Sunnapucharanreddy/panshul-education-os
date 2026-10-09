import pytest

from app.core.exceptions import AuthError
from app.core.security import create_access_token, create_refresh_token, decode_token


def test_access_token_roundtrip():
    token = create_access_token("user-123")
    assert decode_token(token, "access") == "user-123"


def test_refresh_token_wrong_type_rejected():
    token = create_refresh_token("user-123")
    with pytest.raises(AuthError):
        decode_token(token, "access")


def test_garbage_token_rejected():
    with pytest.raises(AuthError):
        decode_token("not-a-token")

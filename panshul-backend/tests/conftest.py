import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ENV", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def anyio_backend():
    return "asyncio"

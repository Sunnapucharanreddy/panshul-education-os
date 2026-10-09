"""One-shot, non-destructive bootstrap for the existing SQLAlchemy schema.

Run with ``python -m app.db.bootstrap`` after configuring the normal backend
environment. ``create_all`` creates missing tables; it does not alter existing
tables or remove data, so schema changes still require an explicit migration.
"""

import asyncio

# Import every mapped model so all existing tables are registered on Base.
from app.db.models import learning as _learning  # noqa: F401
from app.db.models import user as _user  # noqa: F401
from app.db.base import Base
from app.db.session import engine


async def main() -> None:
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()

    tables = ", ".join(sorted(Base.metadata.tables))
    print(f"Database schema is ready. Existing application tables: {tables}")


if __name__ == "__main__":
    asyncio.run(main())

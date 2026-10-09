from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_phone(self, phone: str) -> User | None:
        res = await self.db.execute(select(User).where(User.phone == phone))
        return res.scalar_one_or_none()

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.db.get(User, user_id)

    async def get_or_create(self, phone: str) -> User:
        user = await self.get_by_phone(phone)
        if user is None:
            user = User(phone=phone)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        return user

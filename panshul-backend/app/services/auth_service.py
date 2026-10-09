"""Mobile OTP -> JWT pair. Routes call this; this calls OTP service + user repo."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, decode_token
from app.repositories.user_repo import UserRepository
from app.services.otp_service import OTPService


class AuthService:
    def __init__(self, db: AsyncSession, otp_service: OTPService) -> None:
        self.users = UserRepository(db)
        self.otp = otp_service

    async def request_otp(self, phone: str) -> None:
        await self.otp.request_otp(phone)

    async def verify_and_login(self, phone: str, otp: str) -> dict:
        await self.otp.verify_otp(phone, otp)
        user = await self.users.get_or_create(phone)
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "user_id": user.id,
            "is_new_user": user.name is None,
        }

    async def refresh(self, refresh_token: str) -> dict:
        user_id = decode_token(refresh_token, expected_type="refresh")
        return {"access_token": create_access_token(user_id)}

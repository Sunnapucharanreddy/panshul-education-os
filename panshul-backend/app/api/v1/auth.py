from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.schemas.auth import AccessToken, OTPRequest, OTPVerify, RefreshRequest, TokenPair
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/otp/request", status_code=status.HTTP_202_ACCEPTED,
             summary="Send a 6-digit OTP to a mobile number")
async def request_otp(body: OTPRequest,
                      auth: Annotated[AuthService, Depends(get_auth_service)]):
    await auth.request_otp(body.phone)
    return {"message": "OTP sent"}


@router.post("/otp/verify", response_model=TokenPair,
             summary="Verify OTP and receive JWT tokens")
async def verify_otp(body: OTPVerify,
                     auth: Annotated[AuthService, Depends(get_auth_service)]):
    return await auth.verify_and_login(body.phone, body.otp)


@router.post("/refresh", response_model=AccessToken)
async def refresh(body: RefreshRequest,
                  auth: Annotated[AuthService, Depends(get_auth_service)]):
    return await auth.refresh(body.refresh_token)

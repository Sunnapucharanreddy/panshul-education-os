from pydantic import BaseModel, Field, field_validator


class OTPRequest(BaseModel):
    phone: str = Field(..., examples=["+919876543210"])

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, v: str) -> str:
        cleaned = v.replace(" ", "")
        if not cleaned.startswith("+") or not cleaned[1:].isdigit() or not (10 <= len(cleaned) <= 16):
            raise ValueError("Phone must be E.164, e.g. +919876543210")
        return cleaned


class OTPVerify(OTPRequest):
    otp: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    is_new_user: bool
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"

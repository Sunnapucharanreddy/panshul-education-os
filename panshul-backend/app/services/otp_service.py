"""Phone OTP lifecycle using the selected local or managed SMS verification provider."""
import hashlib
import hmac
import logging
import secrets
from typing import Any
from urllib.parse import quote

import httpx
import redis.asyncio as redis

from app.core.config import get_settings
from app.core.exceptions import AuthError, ProviderError, RateLimited

logger = logging.getLogger(__name__)


class ConsoleSMSGateway:
    async def send(self, phone: str, otp: str) -> None:
        logger.info("DEV OTP for %s: %s", phone, otp)


class TwilioVerifySMSGateway:
    """SMS verification using Twilio Verify v2; Twilio generates and checks codes."""

    BASE_URL = "https://verify.twilio.com/v2/Services"

    def __init__(self, settings: Any, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.settings = settings
        self.transport = transport

    def _credentials(self) -> tuple[str, str, str]:
        values = (self.settings.twilio_api_key_sid,
                  self.settings.twilio_api_secret,
                  self.settings.twilio_verify_service_sid)
        if not all(values):
            raise ProviderError("Twilio SMS verification is not configured on the server.")
        api_key_sid, api_secret, service_sid = values
        return api_key_sid, api_secret, service_sid

    async def _post(self, action: str, data: dict[str, str]) -> dict[str, Any]:
        api_key_sid, api_secret, service_sid = self._credentials()
        # Twilio Verify v2 is scoped by the account-associated service SID; API key
        # SID and secret authenticate the raw REST request with HTTP Basic auth.
        url = f"{self.BASE_URL}/{quote(service_sid, safe='')}/{action}"
        try:
            async with httpx.AsyncClient(timeout=10.0, transport=self.transport) as client:
                response = await client.post(
                    url,
                    data=data,
                    auth=(api_key_sid, api_secret),
                )
        except httpx.RequestError as exc:
            logger.warning("Twilio Verify request failed (%s)", type(exc).__name__)
            raise ProviderError("SMS verification is temporarily unavailable.") from exc

        if response.status_code == 429:
            raise RateLimited("Too many verification requests. Please wait before trying again.")
        if response.is_error:
            try:
                twilio_code = response.json().get("code")
            except (ValueError, AttributeError):
                twilio_code = None
            logger.warning("Twilio Verify returned HTTP %s (code=%s)", response.status_code, twilio_code)
            # Expired or consumed verification attempts are reported by Twilio as 404.
            if action == "VerificationCheck" and response.status_code == 404:
                return {"status": "expired"}
            raise ProviderError("SMS verification is temporarily unavailable.")

        try:
            result = response.json()
        except ValueError as exc:
            logger.warning("Twilio Verify returned an invalid response")
            raise ProviderError("SMS verification returned an invalid response.") from exc
        return result if isinstance(result, dict) else {}

    async def send(self, phone: str) -> None:
        await self._post("Verifications", {"To": phone, "Channel": "sms"})

    async def verify(self, phone: str, otp: str) -> bool:
        result = await self._post("VerificationCheck", {"To": phone, "Code": otp})
        return result.get("status") == "approved"


def get_sms_gateway(settings: Any | None = None) -> ConsoleSMSGateway | TwilioVerifySMSGateway:
    settings = settings or get_settings()
    provider = settings.sms_provider.strip().lower()
    if provider == "console":
        return ConsoleSMSGateway()
    if provider == "twilio":
        return TwilioVerifySMSGateway(settings)
    raise ValueError(f"Unsupported SMS_PROVIDER: {provider}")


class OTPService:
    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client
        self.settings = get_settings()
        self.gateway = get_sms_gateway(self.settings)

    def _hash(self, otp: str) -> str:
        return hmac.new(self.settings.secret_key.encode(), otp.encode(),
                        hashlib.sha256).hexdigest()

    async def request_otp(self, phone: str) -> None:
        attempts_key = f"otp:req:{phone}"
        count = await self.redis.incr(attempts_key)
        if count == 1:
            await self.redis.expire(attempts_key, 3600)
        if count > self.settings.otp_max_attempts:
            raise RateLimited("Too many OTP requests. Try again later.")

        if self.settings.sms_provider.strip().lower() == "twilio":
            # Store no code locally: Twilio Verify owns code generation, expiry, and checks.
            marker_key = f"otp:requested:{phone}"
            await self.redis.set(marker_key, "1", ex=self.settings.otp_ttl_seconds)
            try:
                if not isinstance(self.gateway, TwilioVerifySMSGateway):
                    raise ProviderError("Twilio SMS verification is not configured on the server.")
                await self.gateway.send(phone)
            except Exception:
                await self.redis.delete(marker_key)
                raise
            await self.redis.delete(f"otp:code:{phone}")
            return

        otp = f"{secrets.randbelow(1_000_000):06d}"
        await self.redis.set(f"otp:code:{phone}", self._hash(otp),
                             ex=self.settings.otp_ttl_seconds)
        if not isinstance(self.gateway, ConsoleSMSGateway):
            raise ProviderError("The configured SMS provider is unavailable.")
        await self.gateway.send(phone, otp)

    async def verify_otp(self, phone: str, otp: str) -> bool:
        if self.settings.sms_provider.strip().lower() == "twilio":
            marker_key = f"otp:requested:{phone}"
            if await self.redis.get(marker_key) is None:
                raise AuthError("OTP expired or not requested")
            if not isinstance(self.gateway, TwilioVerifySMSGateway):
                raise ProviderError("Twilio SMS verification is not configured on the server.")
            if not await self.gateway.verify(phone, otp):
                raise AuthError("Invalid or expired OTP")
            await self.redis.delete(marker_key)
            return True

        stored = await self.redis.get(f"otp:code:{phone}")
        if stored is None:
            raise AuthError("OTP expired or not requested")
        if not hmac.compare_digest(stored.decode() if isinstance(stored, bytes) else stored,
                                   self._hash(otp)):
            raise AuthError("Invalid OTP")
        await self.redis.delete(f"otp:code:{phone}")
        return True

from types import SimpleNamespace
from urllib.parse import parse_qs

import httpx
import pytest

from app.services import otp_service
from app.services.otp_service import OTPService, TwilioVerifySMSGateway


def twilio_settings(**overrides):
    values = {
        "sms_provider": "twilio",
        "secret_key": "test-secret",
        "otp_ttl_seconds": 300,
        "otp_max_attempts": 5,
        "twilio_api_key_sid": "SKtest-key",
        "twilio_api_secret": "test-api-secret",
        "twilio_verify_service_sid": "VAtest-service",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


@pytest.mark.asyncio
async def test_twilio_gateway_uses_verify_v2_and_api_key_auth():
    requests = []

    async def handle(request):
        requests.append(request)
        if request.url.path.endswith("/Verifications"):
            return httpx.Response(201, json={"status": "pending"})
        return httpx.Response(200, json={"status": "approved", "valid": True})

    gateway = TwilioVerifySMSGateway(
        twilio_settings(), transport=httpx.MockTransport(handle)
    )
    await gateway.send("+919876543210")
    assert await gateway.verify("+919876543210", "123456") is True

    assert requests[0].method == "POST"
    assert requests[0].url.path.endswith("/v2/Services/VAtest-service/Verifications")
    assert parse_qs(requests[0].content.decode()) == {
        "To": ["+919876543210"], "Channel": ["sms"]
    }
    assert requests[1].url.path.endswith("/VerificationCheck")
    assert parse_qs(requests[1].content.decode()) == {
        "To": ["+919876543210"], "Code": ["123456"]
    }
    assert requests[0].headers["Authorization"].startswith("Basic ")


@pytest.mark.asyncio
async def test_twilio_pending_check_is_not_accepted():
    async def handle(_request):
        return httpx.Response(200, json={"status": "pending", "valid": False})

    gateway = TwilioVerifySMSGateway(
        twilio_settings(), transport=httpx.MockTransport(handle)
    )
    assert await gateway.verify("+919876543210", "000000") is False


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.counts = {}

    async def incr(self, key):
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, _key, _seconds):
        return True

    async def set(self, key, value, ex=None):
        self.values[key] = value
        return True

    async def get(self, key):
        return self.values.get(key)

    async def delete(self, key):
        self.values.pop(key, None)
        return 1


class FakeTwilioGateway(TwilioVerifySMSGateway):
    def __init__(self):
        self.sent = []
        self.is_valid = True

    async def send(self, phone):
        self.sent.append(phone)

    async def verify(self, _phone, _otp):
        return self.is_valid


@pytest.mark.asyncio
async def test_twilio_service_stores_no_otp_and_clears_marker_after_approval(monkeypatch):
    settings = twilio_settings()
    gateway = FakeTwilioGateway()
    monkeypatch.setattr(otp_service, "get_settings", lambda: settings)
    monkeypatch.setattr(otp_service, "get_sms_gateway", lambda _settings: gateway)
    redis = FakeRedis()
    service = OTPService(redis)
    phone = "+919876543210"

    await service.request_otp(phone)
    assert gateway.sent == [phone]
    assert redis.values == {f"otp:requested:{phone}": "1"}

    assert await service.verify_otp(phone, "123456") is True
    assert redis.values == {}

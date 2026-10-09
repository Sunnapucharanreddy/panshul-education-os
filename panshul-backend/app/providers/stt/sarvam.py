"""Sarvam AI (Saarika) STT adapter — API-based, no GPU needed.
Strong on Indian languages + code-mixed speech. Set STT_PROVIDER=sarvam."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import STTProvider, Transcript


class SarvamSTTProvider(STTProvider):
    def __init__(self) -> None:
        s = get_settings()
        if not s.sarvam_api_key:
            raise ProviderError("SARVAM_API_KEY not set")
        self._model = s.sarvam_stt_model
        self._client = httpx.AsyncClient(
            base_url="https://api.sarvam.ai",
            headers={"api-subscription-key": s.sarvam_api_key},
            timeout=120,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    async def transcribe(self, audio_bytes: bytes, *, language: str | None = None) -> Transcript:
        data = {"model": self._model}
        if language:
            data["language_code"] = language
        try:
            resp = await self._client.post(
                "/speech-to-text",
                data=data,
                files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            )
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Sarvam STT failed: {exc}") from exc
        payload = resp.json()
        lang = (payload.get("language_code") or "en-IN").split("-")[0]
        return Transcript(text=payload.get("transcript", ""), language=lang,
                          duration_seconds=0.0)

"""Sarvam AI (Bulbul) TTS adapter — API-based, no GPU needed.
Native Telugu/Hindi/English with code-switching. Set TTS_PROVIDER=sarvam."""
import base64

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import TTSProvider

# Map our internal language hints to Sarvam BCP-47 codes.
LANG_MAP = {
    "en": "en-IN", "te": "te-IN", "hi": "hi-IN", "ta": "ta-IN",
    "kn": "kn-IN", "ml": "ml-IN", "bn": "bn-IN", "mr": "mr-IN",
    "gu": "gu-IN", "pa": "pa-IN", "od": "od-IN",
}


class SarvamTTSProvider(TTSProvider):
    def __init__(self) -> None:
        s = get_settings()
        if not s.sarvam_api_key:
            raise ProviderError("SARVAM_API_KEY not set")
        self._speaker = s.sarvam_tts_speaker
        self._model = s.sarvam_tts_model
        self._client = httpx.AsyncClient(
            base_url="https://api.sarvam.ai",
            headers={"api-subscription-key": s.sarvam_api_key},
            timeout=60,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    async def synthesize(self, text: str, *, language: str = "en",
                         voice: str | None = None) -> bytes:
        lang_code = LANG_MAP.get(language.split("-")[0].lower(), "en-IN")
        try:
            resp = await self._client.post("/text-to-speech", json={
                "text": text,
                "target_language_code": lang_code,
                "speaker": voice or self._speaker,
                "model": self._model,
            })
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise ProviderError(f"Sarvam TTS failed: {exc}") from exc
        audios = resp.json().get("audios") or []
        if not audios:
            raise ProviderError("Sarvam TTS returned no audio")
        return base64.b64decode(audios[0])

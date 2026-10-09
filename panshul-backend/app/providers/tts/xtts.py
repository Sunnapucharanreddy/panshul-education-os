"""Coqui XTTS v2 adapter. Same lazy-load pattern as STT."""
import asyncio
import io

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import TTSProvider


class XTTSProvider(TTSProvider):
    def __init__(self) -> None:
        self._tts = None

    def _load(self):
        if self._tts is None:
            try:
                from TTS.api import TTS
            except ImportError as exc:
                raise ProviderError("Coqui TTS not installed on this worker") from exc
            self._tts = TTS(model_path=get_settings().tts_model_path)
        return self._tts

    async def synthesize(self, text: str, *, language: str = "en",
                         voice: str | None = None) -> bytes:
        def _run() -> bytes:
            import soundfile as sf
            tts = self._load()
            wav = tts.tts(text=text, language=language, speaker=voice)
            buf = io.BytesIO()
            sf.write(buf, wav, 24000, format="WAV")
            return buf.getvalue()

        return await asyncio.to_thread(_run)

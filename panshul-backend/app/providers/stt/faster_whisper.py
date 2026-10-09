"""Faster-Whisper STT adapter. Model loads lazily on first use so the API
process can start without GPU deps installed (voice runs on a worker)."""
import asyncio
import io

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import STTProvider, Transcript


class FasterWhisperProvider(STTProvider):
    def __init__(self) -> None:
        self._model = None

    def _load(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise ProviderError("faster-whisper not installed on this worker") from exc
            self._model = WhisperModel(get_settings().stt_model, device="auto")
        return self._model

    async def transcribe(self, audio_bytes: bytes, *, language: str | None = None) -> Transcript:
        def _run() -> Transcript:
            model = self._load()
            segments, info = model.transcribe(io.BytesIO(audio_bytes), language=language)
            text = " ".join(seg.text.strip() for seg in segments)
            return Transcript(text=text, language=info.language, duration_seconds=info.duration)

        return await asyncio.to_thread(_run)

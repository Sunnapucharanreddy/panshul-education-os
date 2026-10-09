"""Voice pipeline: audio -> STT -> orchestrator -> TTS -> audio.
The avatar client (Live2D) plays the returned audio + lip-syncs to it."""
import base64
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.deps import get_conversation_service, get_current_user_id
from app.providers.registry import get_stt, get_tts
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/converse", summary="Voice in, voice out (avatar conversation)")
async def voice_converse(
    user_id: Annotated[str, Depends(get_current_user_id)],
    svc: Annotated[ConversationService, Depends(get_conversation_service)],
    audio: UploadFile = File(...),
    session_id: str | None = Form(None),
    language: str | None = Form(None),
):
    transcript = await get_stt().transcribe(await audio.read(), language=language)
    result = await svc.send_message(user_id, transcript.text, session_id)
    audio_bytes = await get_tts().synthesize(result["response"],
                                             language=transcript.language or "en")
    return {
        **result,
        "transcript": transcript.text,
        "audio_base64": base64.b64encode(audio_bytes).decode(),
        "audio_format": "wav",
    }

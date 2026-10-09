"""Qwen 3 adapter over any OpenAI-compatible endpoint (Groq, vLLM, OpenRouter,
DashScope...). Pointing LLM_BASE_URL at a different server swaps the backend
with zero code changes.

Qwen 3 is a hybrid-reasoning model: some servers return its chain-of-thought
wrapped in <think>...</think>. We strip that so it never leaks to students."""
import json
import logging
import re
from typing import AsyncIterator

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import ProviderError
from app.providers.base import ChatMessage, LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


_THINK_RE = re.compile(r"<think>.*?</think>\s*", re.DOTALL)


def strip_reasoning(text: str) -> str:
    """Remove Qwen3 <think> blocks (and an unclosed leading one) from output."""
    text = _THINK_RE.sub("", text)
    if text.lstrip().startswith("<think>"):
        text = text.split("</think>")[-1]
    return text.strip()


def _extract_error_detail(exc: httpx.HTTPError) -> str:
    """Extract informative error text from HTTP response if available."""
    if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
        try:
            data = exc.response.json()
            if isinstance(data, dict):
                err = data.get("error")
                if isinstance(err, dict) and "message" in err:
                    return f"{exc.response.status_code} - {err['message']}"
                elif isinstance(err, str):
                    return f"{exc.response.status_code} - {err}"
        except Exception:
            pass
        return f"{exc.response.status_code} - {exc.response.text.strip()}"
    return str(exc)


def _is_retryable_error(exc: BaseException) -> bool:
    """Do not retry deterministic 4xx client errors (e.g. 401 invalid key, 400 bad request, 404).

    Only retry transient network glitches, 5xx server errors, or 429 rate limits.
    """
    if isinstance(exc, ProviderError) and isinstance(exc.__cause__, httpx.HTTPStatusError):
        code = exc.__cause__.response.status_code
        if 400 <= code < 500 and code != 429:
            return False
    return True


class QwenProvider(LLMProvider):
    def __init__(self) -> None:
        s = get_settings()
        self._model = s.llm_model
        self._client = httpx.AsyncClient(
            base_url=s.llm_base_url,
            headers={"Authorization": f"Bearer {s.llm_api_key}"},
            timeout=s.llm_timeout_seconds,
        )

    @retry(
        retry=retry_if_exception(_is_retryable_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=8),
        reraise=True,
    )
    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.7,
                   max_tokens: int = 1024, json_mode: bool = False) -> LLMResponse:
        body: dict = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        if "groq.com" in str(self._client.base_url):
            # Groq-specific: keep Qwen3 reasoning out of the response payload.
            body["reasoning_format"] = "hidden"
        try:
            resp = await self._client.post("/chat/completions", json=body)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            detail = _extract_error_detail(exc)
            logger.error("LLM request failed: %s", detail)
            raise ProviderError(f"LLM request failed ({detail})") from exc
        data = resp.json()
        return LLMResponse(
            content=strip_reasoning(data["choices"][0]["message"]["content"]),
            model=data.get("model", self._model),
            usage=data.get("usage", {}),
        )

    async def stream(self, messages: list[ChatMessage], *, temperature: float = 0.7,
                     max_tokens: int = 1024) -> AsyncIterator[str]:
        body = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        try:
            async with self._client.stream("POST", "/chat/completions", json=body) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    chunk = line[6:]
                    if chunk.strip() == "[DONE]":
                        break
                    delta = json.loads(chunk)["choices"][0]["delta"].get("content")
                    if delta:
                        yield delta
        except httpx.HTTPError as exc:
            detail = _extract_error_detail(exc)
            logger.error("LLM streaming failed: %s", detail)
            raise ProviderError(f"LLM streaming failed ({detail})") from exc


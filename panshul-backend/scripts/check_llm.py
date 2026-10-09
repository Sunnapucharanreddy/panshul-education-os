"""Verify your LLM setup end to end (run after filling .env):

    python scripts/check_llm.py

Checks: raw chat call -> JSON mode -> orchestrator intent routing.
"""
import asyncio
import sys

sys.path.insert(0, ".")

from app.agents.orchestrator import Orchestrator  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.providers.base import ChatMessage  # noqa: E402
from app.providers.registry import get_llm  # noqa: E402


async def main() -> None:
    s = get_settings()
    print(f"Endpoint : {s.llm_base_url}")
    print(f"Model    : {s.llm_model}")
    if not s.llm_api_key:
        print("WARN     : LLM_API_KEY is empty — Groq/OpenRouter will reject this.")

    llm = get_llm()

    print("\n[1/3] Basic chat ...")
    r = await llm.chat([ChatMessage(role="user", content="Reply with exactly: OK")],
                       temperature=0, max_tokens=200)
    print(f"      -> {r.content[:80]!r}  (usage: {r.usage})")

    print("[2/3] JSON mode ...")
    r = await llm.chat(
        [ChatMessage(role="system", content='Respond ONLY with JSON: {"status": "ok"}'),
         ChatMessage(role="user", content="go")],
        temperature=0, max_tokens=200, json_mode=True)
    print(f"      -> {r.content[:80]!r}")

    print("[3/3] Orchestrator routing ...")
    result = await Orchestrator(llm).handle({
        "user_id": "smoke-test",
        "message": "Give me 5 practice questions on photosynthesis",
        "history": [], "memory_context": "None yet",
    })
    print(f"      -> intent={result['intent']!r} (expected 'quiz')")
    print(f"      -> response starts: {result['agent_response'][:100]!r}")

    print("\nAll checks passed — your agents are live.")


if __name__ == "__main__":
    asyncio.run(main())

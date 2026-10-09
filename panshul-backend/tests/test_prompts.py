from app.prompts.loader import get_prompt


def test_all_agent_prompts_load():
    for agent in ("orchestrator", "teacher", "quiz", "career", "interview", "startup"):
        assert len(get_prompt(agent, "system", memory_context="x")
                   if agent != "orchestrator" else get_prompt(agent)) > 50


def test_memory_context_injected():
    text = get_prompt("teacher", "system", memory_context="Weak in algebra")
    assert "Weak in algebra" in text

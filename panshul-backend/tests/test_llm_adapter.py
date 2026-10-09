from app.providers.llm.qwen import strip_reasoning


def test_strips_think_block():
    raw = "<think>reasoning here...</think>The answer is 42."
    assert strip_reasoning(raw) == "The answer is 42."


def test_plain_text_untouched():
    assert strip_reasoning("Hello student!") == "Hello student!"


def test_multiline_think():
    raw = "<think>\nline1\nline2\n</think>\n\nFinal reply."
    assert strip_reasoning(raw) == "Final reply."

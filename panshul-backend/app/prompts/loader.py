"""Prompt loader — prompts are versioned YAML data, never Python strings.
Each file: prompts/<agent>.yaml with keys: system, and optional named templates.
Templates use str.format placeholders."""
from functools import lru_cache
from pathlib import Path

import yaml

from app.core.config import get_settings
from app.core.exceptions import NotFoundError


@lru_cache
def _load(agent: str) -> dict:
    path = Path(get_settings().prompts_dir) / f"{agent}.yaml"
    if not path.exists():
        raise NotFoundError(f"Prompt file missing: {path}")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_prompt(agent: str, key: str = "system", **kwargs) -> str:
    data = _load(agent)
    template = data.get(key)
    if template is None:
        raise NotFoundError(f"Prompt key '{key}' not found for agent '{agent}'")
    return template.format(**kwargs) if kwargs else template

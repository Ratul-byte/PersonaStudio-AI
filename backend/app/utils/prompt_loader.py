"""Loads prompt templates from disk.

Prompts are never hardcoded inside Python modules — they live as plain-text
files under ``app/prompts/`` so they can be edited, versioned, and reused
without touching application code.
"""
import os
from functools import lru_cache

_PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


@lru_cache(maxsize=64)
def load_prompt(name: str) -> str:
    """Load a prompt template by name (without the .txt extension).

    Args:
        name: Filename stem of the prompt, e.g. ``"formal"`` loads
            ``app/prompts/formal.txt``.

    Returns:
        The raw template text, with ``{placeholders}`` intact for
        ``str.format`` substitution by the caller.
    """
    path = os.path.join(_PROMPTS_DIR, f"{name}.txt")
    if not os.path.exists(path):
        path = os.path.join(_PROMPTS_DIR, "default.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

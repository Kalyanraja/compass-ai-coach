"""Optional LLM enhancer (off by default).

Compass is fully deterministic and works offline with no API keys. If an
organization later approves a model endpoint (for example a local model server
or an internal gateway exposing an OpenAI-compatible /v1/chat/completions API),
set COMPASS_LLM_URL and COMPASS_LLM_MODEL. The enhancer only rewords a prompt the
deterministic coach already produced; it never sees signals data, never stores
anything, and failures fall back silently to the deterministic output.
"""

from __future__ import annotations

import json
import urllib.request

from . import config


def enabled() -> bool:
    return bool(config.LLM_URL and config.LLM_MODEL)


def polish(prompt: str, timeout: float = 20.0) -> str | None:
    if not enabled():
        return None
    body = json.dumps({
        "model": config.LLM_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": "Tighten this coding-agent prompt. Keep every requirement, constraint and question. "
                                          "Do not invent requirements. Return only the prompt."},
            {"role": "user", "content": prompt},
        ],
    }).encode()
    req = urllib.request.Request(config.LLM_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        return data["choices"][0]["message"]["content"].strip()
    except Exception:  # noqa: BLE001 - optional feature must never break the coach
        return None

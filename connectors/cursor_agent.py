from __future__ import annotations

import os
from pathlib import Path


def ask_cursor(prompt: str) -> str:
    try:
        from cursor_sdk import Agent, CursorAgentError, LocalAgentOptions
    except ImportError as exc:
        raise RuntimeError(
            "cursor-sdk is not installed. Run: .venv\\Scripts\\python.exe -m pip install cursor-sdk"
        ) from exc

    api_key = os.getenv("CURSOR_API_KEY")
    if not api_key:
        raise RuntimeError(
            "CURSOR_API_KEY missing. Copy .env.example to .env and add your Cursor key."
        )

    model = os.getenv("CURSOR_MODEL", "composer-2.5")
    workspace = Path(__file__).resolve().parents[1]

    try:
        with Agent.create(
            model=model,
            api_key=api_key,
            local=LocalAgentOptions(cwd=str(workspace)),
        ) as agent:
            run = agent.send(prompt)
            result = run.wait()
            if result.status == "error":
                raise RuntimeError(f"Cursor run failed: {result.id}")
            return run.text()
    except CursorAgentError as err:
        raise RuntimeError(
            f"Cursor did not start: {err.message} (retryable={err.is_retryable})"
        ) from err

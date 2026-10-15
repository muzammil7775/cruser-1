"""Cruser: one Python app connected to Cursor Agent and ChatGPT."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from connectors.chatgpt import ask_chatgpt
from connectors.cursor_agent import ask_cursor

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/status")
def status():
    return jsonify(
        {
            "python": True,
            "cursor": bool(os.getenv("CURSOR_API_KEY")),
            "chatgpt": bool(os.getenv("OPENAI_API_KEY")),
        }
    )


@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    provider = (data.get("provider") or "chatgpt").strip().lower()

    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400

    try:
        if provider == "cursor":
            text = ask_cursor(prompt)
        elif provider == "chatgpt":
            text = ask_chatgpt(prompt)
        else:
            return jsonify({"error": "Use provider 'cursor' or 'chatgpt'."}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"provider": provider, "reply": text})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

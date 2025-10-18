#!/usr/bin/env python3
"""
OpenAI Smoke Test (SDK)
-----------------------
Uses OPENAI_API_KEY from .env to call OpenAI Chat Completions via the official SDK.
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

try:
    from backend.config_init import ensure_config_loaded
    ensure_config_loaded(verbose=False)
except Exception:
    pass

from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("FAIL: OPENAI_API_KEY is not set")
    sys.exit(1)

client = OpenAI(api_key=api_key)

try:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Respond only with the word: pong"}],
        temperature=0,
    )
    content = resp.choices[0].message.content.strip()
    print(f"OK: {content}")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)

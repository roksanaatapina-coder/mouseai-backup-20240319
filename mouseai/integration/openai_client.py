import os
import json
import requests
from typing import Dict, Any


def openai_analysis(prompt: str, api_key: str = None, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a gamer mouse sensitivity optimizator."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 450,
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

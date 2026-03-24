import os
import json
from typing import Dict, Any
import requests

from mouseai.integration.openai_client import openai_analysis
from mouseai.integration.serpapi_client import serpapi_about_carousel


def get_env_key(name: str) -> str:
    value = os.getenv(name, "")
    if not value:
        raise ValueError(f"Environment variable {name} is not set")
    return value


class AISync:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY", "")
        self.cohere_key = os.getenv("COHERE_API_KEY", "")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    def sync_data(self, query: str = "mouse sensitivity gaming") -> Dict[str, Any]:
        result: Dict[str, Any] = {"query": query}

        try:
            result["serpapi"] = serpapi_about_carousel(query, api_key=self.serpapi_key)
        except Exception as e:
            result["serpapi_error"] = str(e)

        ai_input = f"Используя результаты Search API, сформируй рекомендации для оптимальной настройки мыши в играх. СерпAPI: {json.dumps(result.get('serpapi', {}), ensure_ascii=False)}"

        try:
            result["openai"] = openai_analysis(ai_input, api_key=self.openai_key)
        except Exception as e:
            result["openai_error"] = str(e)

        # Добавьте дополнительные интеграции, если нужно
        return result


def run_full_pipeline(query: str = "mouse sensitivity gaming") -> Dict[str, Any]:
    syncer = AISync()
    return syncer.sync_data(query)

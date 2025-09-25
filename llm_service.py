import os
import json
from typing import List, Dict, Any, Optional

import httpx


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")


def _get_headers() -> Dict[str, str]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY environment variable")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _post_chat(payload: Dict[str, Any]) -> Dict[str, Any]:
    with httpx.Client(timeout=30) as client:
        response = client.post(OPENROUTER_API_URL, headers=_get_headers(), json=payload)
        response.raise_for_status()
        return response.json()


def llm_chat(messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.2) -> str:
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    data = _post_chat(payload)
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Unexpected LLM response shape: {data}") from exc


def llm_json(messages: List[Dict[str, str]], model: Optional[str] = None, temperature: float = 0.0) -> Dict[str, Any]:
    system_json_instruction = (
        "You must answer ONLY with a single valid JSON object. Do not include any prose."
    )
    msgs = []
    # Ensure the JSON-only constraint is present
    if not any(m.get("role") == "system" for m in messages):
        msgs.append({"role": "system", "content": system_json_instruction})
    else:
        # Prepend our instruction to be safe
        msgs.append({"role": "system", "content": system_json_instruction})
    msgs.extend(messages)

    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": msgs,
        "temperature": temperature,
        # OpenRouter supports OpenAI-compatible params; JSON mode via strict system instruction
    }
    data = _post_chat(payload)
    try:
        content = data["choices"][0]["message"]["content"].strip()
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"LLM did not return valid JSON: {content}") from exc
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Unexpected LLM response shape: {data}") from exc



from __future__ import annotations

import argparse
import json
from typing import Dict, Any

try:
    # When executed as a package module
    from .llm_service import llm_chat, llm_json
except Exception:  # noqa: BLE001
    # When executed directly: python main.py
    from llm_service import llm_chat, llm_json  # type: ignore


def sum_integers(a: int, b: int) -> int:
    return int(a) + int(b)


def praise_user() -> str:
    return "You're the best !"


INTENT_SYSTEM_PROMPT = (
    """
You are an intent router. Decide how to handle the user's prompt using JSON in your response.
Return ONLY a JSON object with fields: {"route": "sum|praise|general", "a": int?, "b": int?}.
Rules:
- If the user asks to add or sum two integers, set route="sum" and extract integers a and b.
- If the user asks for praise, compliments, motivation, or similar, set route="praise".
- Otherwise, set route="general".
    """
).strip()


def route_intent(user_prompt: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    data = llm_json(messages)
    # Normalize and validate
    route = str(data.get("route", "general")).lower()
    if route not in {"sum", "praise", "general"}:
        route = "general"
    result = {"route": route}
    if route == "sum":
        try:
            result["a"] = int(data.get("a"))
            result["b"] = int(data.get("b"))
        except Exception:
            result["route"] = "general"
    return result


def generate_general_response(user_prompt: str) -> str:
    system = (
        "You are a concise helpful assistant. Answer the user's question briefly and clearly."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt},
    ]
    return llm_chat(messages)


def agent_respond(user_prompt: str) -> str:
    decision = route_intent(user_prompt)
    route = decision["route"]
    if route == "sum":
        return str(sum_integers(decision["a"], decision["b"]))
    if route == "praise":
        return praise_user()
    return generate_general_response(user_prompt)


def cli() -> None:
    parser = argparse.ArgumentParser(description="Simple AI Agent CLI")
    parser.add_argument("prompt", nargs="*", help="User prompt")
    args = parser.parse_args()
    if not args.prompt:
        print("Please provide a prompt.")
        return
    prompt = " ".join(args.prompt)
    print(agent_respond(prompt))


if __name__ == "__main__":
    cli()



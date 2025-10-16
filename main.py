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
You are an intent router that determines which action tool to execute based on the user's request.
Analyze the user's input and decide which of the following action tools should be invoked:

Available action tools:
1. "sum" - Executes the sum_integers action tool to add two integers together
2. "praise" - Executes the praise_user action tool to provide encouragement and motivation
3. "general" - Executes the general response action tool for all other queries

Return ONLY a JSON object with fields: {"action": "sum|praise|general", "a": int?, "b": int?}.

Rules:
- If the user asks to add or sum two integers, set action="sum" and extract integers a and b. This will trigger the sum_integers action tool.
- If the user asks for praise, compliments, motivation, or similar, set action="praise". This will trigger the praise_user action tool.
- Otherwise, set action="general". This will trigger the general response action tool.

Your response will determine which action tool gets executed next.
    """
).strip()
def route_intent(user_prompt: str) -> Dict[str, Any]:
    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    data = llm_json(messages)
    # Normalize and validate
    action = str(data.get("action", "general")).lower()
    if action not in {"sum", "praise", "general"}:
        action = "general"
    result = {"route": action}
    if action == "sum":
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

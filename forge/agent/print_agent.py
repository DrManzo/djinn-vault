#!/usr/bin/env python3
"""
Djinn Print Agent — runs on Typhon.
Drives qwen2.5-coder:7b via Ollama to handle end-to-end 3D printing.

Usage:
    python3 print_agent.py
    python3 print_agent.py "make a 40mm cube with a 10mm hole through the center"

Setup (first time on Typhon):
    ollama pull qwen2.5-coder:7b
    pip3 install ollama requests
"""

import sys, json
import ollama

from system_prompt import SYSTEM_PROMPT
from tools import TOOLS, run_tool

MODEL = "qwen2.5-coder:7b"


def chat(messages: list) -> dict:
    return ollama.chat(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        options={"temperature": 0.2, "num_ctx": 8192}
    )


def agent_loop(user_input: str, messages: list) -> str:
    messages.append({"role": "user", "content": user_input})

    while True:
        response = chat(messages)
        msg = response["message"]
        messages.append(msg)

        # No tool calls — final answer
        if not msg.get("tool_calls"):
            return msg.get("content", "")

        # Execute all tool calls
        for tc in msg["tool_calls"]:
            name = tc["function"]["name"]
            args = tc["function"].get("arguments", {})
            if isinstance(args, str):
                args = json.loads(args)

            print(f"\n[tool: {name}]", flush=True)
            if name == "write_and_run":
                print(f"  writing {args.get('filename', '?')} ...", flush=True)

            result = run_tool(name, args)
            print(f"  → {result[:120].strip()}", flush=True)

            messages.append({
                "role": "tool",
                "content": result,
                "name": name
            })


def main():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Single-shot mode
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        answer = agent_loop(prompt, messages)
        print(answer)
        return

    # Interactive loop
    print(f"Djinn Print  [{MODEL}]  type 'exit' to quit\n")
    while True:
        try:
            user = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break
        if not user:
            continue
        if user.lower() in ("exit", "quit", "q"):
            break

        answer = agent_loop(user, messages)
        print(f"\nagent > {answer}\n")


if __name__ == "__main__":
    main()

"""
작업 내용:
- 멀티턴 대화 메모리를 사용하는 CLI 챗봇 스크립트를 추가함.
- /reset, /trim N, /stats, /exit 명령과 토큰/비용 통계를 포함함.

설명:
- OpenAI Chat Completions API를 호출해 대화 히스토리를 유지하며 응답함.
- SYSTEM_PROMPT/OPENAI_MODEL 환경변수와 --system/--model 인자를 지원함.
"""

from __future__ import annotations

import argparse
import os
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI


DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant. If unsure, reply with 'Needs verification'."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multi-turn CLI chatbot with memory.")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--system", default=os.getenv("SYSTEM_PROMPT", ""))
    return parser


class ChatSession:
    def __init__(self, client: OpenAI, model: str, system: str) -> None:
        self.client = client
        self.model = model
        self.system = system
        self.history: List[Dict[str, str]] = []
        self.usage_log: List[int] = []

    def reset(self) -> None:
        self.history.clear()
        self.usage_log.clear()

    def chat(self, message: str, temperature: float = 0.3) -> str:
        self.history.append({"role": "user", "content": message})
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[{"role": "system", "content": self.system}, *self.history],
        )
        answer = resp.choices[0].message.content
        self.history.append({"role": "assistant", "content": answer})
        if resp.usage and resp.usage.total_tokens is not None:
            self.usage_log.append(resp.usage.total_tokens)
        return answer

    def trim(self, keep: int = 6) -> None:
        if keep < 0:
            keep = 0
        self.history = self.history[-keep:]

    def stats(self) -> str:
        price = 0.30 / 1_000_000
        total = sum(self.usage_log)
        if not self.usage_log:
            return "No usage yet."
        per_turn = total / len(self.usage_log)
        estimate = per_turn * 100 * price
        return (
            f"Turn tokens: {self.usage_log}\n"
            f"Total tokens: {total}, Total cost: ${total * price:.5f}\n"
            f"100-turn estimate: ${estimate:.4f} (actual is higher due to history growth)"
        )


def main() -> None:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    system = args.system.strip() if args.system else DEFAULT_SYSTEM_PROMPT

    client = OpenAI()
    session = ChatSession(client=client, model=args.model, system=system)

    print("Multi-turn CLI chatbot. Commands: /help, /reset, /trim N, /stats, /exit")
    while True:
        try:
            text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break

        if not text:
            continue

        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in {"/exit", "/quit"}:
                print("bye")
                break
            if cmd == "/help":
                print("/reset, /trim N, /stats, /exit")
                continue
            if cmd == "/reset":
                session.reset()
                print("(reset)")
                continue
            if cmd == "/trim":
                try:
                    keep = int(arg)
                except ValueError:
                    print("Usage: /trim N")
                    continue
                session.trim(keep=keep)
                print(f"(trimmed to {keep})")
                continue
            if cmd == "/stats":
                print(session.stats())
                continue

            print("Unknown command. Use /help.")
            continue

        answer = session.chat(text, temperature=args.temperature)
        print(f"bot> {answer}")


if __name__ == "__main__":
    main()

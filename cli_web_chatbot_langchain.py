from __future__ import annotations

import argparse

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

MODEL = "gpt-4o-mini"
SYSTEM = "당신은 친절한 AI 어시스턴트입니다. 모르면 '확인 필요'라고만 답하세요."


def build_langchain_messages(history: list[dict[str, str]]) -> list[object]:
    # Convert role/content dicts into LangChain message objects.
    msgs: list[object] = [SystemMessage(content=SYSTEM)]
    for item in history:
        role = item.get("role")
        content = item.get("content", "")
        cls = HumanMessage if role == "user" else AIMessage
        msgs.append(cls(content=content))
    return msgs


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="CLI LangChain chatbot")
    parser.add_argument(
        "message",
        nargs="*",
        help="User message. If omitted, a prompt will appear.",
    )
    args = parser.parse_args()

    llm = ChatOpenAI(model=MODEL, temperature=0.3)
    messages: list[dict[str, str]] = []

    first_message = " ".join(args.message).strip() if args.message else ""
    if first_message:
        messages.append({"role": "user", "content": first_message})

    while True:
        if not messages or messages[-1]["role"] != "user":
            user_message = input("Message (or 'exit'): ").strip()
            if not user_message:
                continue
            if user_message.lower() in {"exit", "quit"}:
                break
            messages.append({"role": "user", "content": user_message})

        msgs = build_langchain_messages(messages)
        answer = llm.invoke(msgs).content
        print(answer)
        messages.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()

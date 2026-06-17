"""멀티턴 메모리 챗봇 (Streamlit UI).

실행:
    streamlit run web/streamlit_memory.py
"""
import os

from dotenv import load_dotenv
import streamlit as st
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
SYSTEM = "당신은 친절한 AI 어시스턴트입니다. 모르면 '확인 필요'라고만 답하세요."

st.set_page_config(page_title="멀티턴 메모리 챗봇")
st.title("멀티턴 메모리 챗봇")

with st.sidebar:
    if st.button("대화 초기화"):
        st.session_state.clear()
        st.rerun()

client = OpenAI()

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.chat_message("assistant").write("안녕하세요! 무엇이든 물어보세요.")

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

user_input = st.chat_input("메시지를 입력하세요")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.chat_message("assistant"):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                temperature=0.3,
                messages=[{"role": "system", "content": SYSTEM}, *st.session_state.messages],
            )
            answer = resp.choices[0].message.content
        except Exception:
            answer = "죄송합니다. 일시적인 오류가 발생했어요. 잠시 후 다시 시도해 주세요."
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

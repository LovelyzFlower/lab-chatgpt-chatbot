"""실습 5 Task 1 — Streamlit 챗봇.

웹 챗봇 골격을 이 저장소 안에서 직접 구현한다.
사이드바: 페르소나 선택 / temperature 슬라이더, 본문: 스트리밍 응답 + 운영 가드.

실행:
    streamlit run web/streamlit_app.py
    # 컨테이너에서 8501 포트가 자동 포워딩된다.
"""
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

SYSTEM = "당신은 친절한 AI 어시스턴트입니다. 모르면 '확인 필요'라고만 답하세요."

st.set_page_config(page_title="나만의 ChatGPT", page_icon="💬")
st.title("나만의 ChatGPT 💬 (Streamlit)")

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.3)

# ── 대화 상태 ─────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []          # [{"role", "content"}]

# 환영 메시지 (처음 1회)
if not st.session_state.messages:
    st.chat_message("assistant").write("안녕하세요! 무엇이든 물어보세요 😊")

for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

user_input = st.chat_input("메시지를 입력하세요")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    # LangChain 메시지로 변환 (system + 누적 history)
    msgs = [SystemMessage(content=SYSTEM)]
    for m in st.session_state.messages:
        cls = HumanMessage if m["role"] == "user" else AIMessage
        msgs.append(cls(content=m["content"]))

    with st.chat_message("assistant"):
        try:
            # 운영 가드 2 — 스트리밍 응답
            def gen():
                for chunk in llm.stream(msgs):
                    yield chunk.content or ""
            answer = st.write_stream(gen())
        except Exception:
            # 운영 가드 3 — Stack trace 노출 금지
            answer = "죄송합니다. 일시적인 오류가 발생했어요. 잠시 후 다시 시도해 주세요."
            st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

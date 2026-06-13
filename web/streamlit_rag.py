"""실습 6 Task 2 — Streamlit + RAG (자체완결).

파일 업로드 → 즉시 RAG 챗봇 생성. 업로드한 문서로만 답하는 RAG 흐름을
이 저장소 안에서 직접 구현한다. (.md / .txt / .pdf 지원)

실행:
    streamlit run web/streamlit_rag.py
    # 컨테이너에서 8501 포트가 자동 포워딩된다.
"""
import tempfile
from pathlib import Path

from dotenv import load_dotenv
import streamlit as st
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

st.set_page_config(page_title="문서 RAG 챗봇", page_icon="📄")
st.title("문서 업로드 → RAG 챗봇 📄")

PROMPT = ChatPromptTemplate.from_template(
    """아래 '문맥'만 근거로 한국어로 답하세요.
문맥에 답이 없으면 반드시 "문서에서 찾을 수 없습니다"라고만 답하세요.

[문맥]
{context}

[질문]
{question}
"""
)


@st.cache_resource(show_spinner="문서 인덱싱 중...")
def build_chain(file_bytes: bytes, suffix: str):
    """업로드 파일 → 청크 → FAISS → RAG 체인. (캐시: 같은 파일은 1회만 인덱싱)"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    loader = PyMuPDFLoader(tmp_path) if suffix == ".pdf" else TextLoader(tmp_path, encoding="utf-8")
    docs = loader.load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100).split_documents(docs)

    vs = FAISS.from_documents(chunks, OpenAIEmbeddings(model="text-embedding-3-small"))
    retriever = vs.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def fmt(ds):
        return "\n\n".join(d.page_content for d in ds)

    return (
        {"context": retriever | fmt, "question": RunnablePassthrough()}
        | PROMPT | llm | StrOutputParser()
    )


uploaded = st.file_uploader("문서 업로드 (.md / .txt / .pdf)", type=["md", "txt", "pdf"])

if not uploaded:
    st.info("문서를 업로드하면 그 내용으로만 답하는 챗봇이 생성됩니다. "
            "샘플: `data/sample_docs/hr_policy.md`")
    st.stop()

chain = build_chain(uploaded.getvalue(), Path(uploaded.name).suffix.lower())
st.success(f"'{uploaded.name}' 인덱싱 완료 — 질문해 보세요.")

question = st.chat_input("문서 내용을 물어보세요")
if question:
    st.chat_message("user").write(question)
    with st.chat_message("assistant"):
        st.write(chain.invoke(question))

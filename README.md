# ChatGPT NLP 실습 (Dev Container)

자연어 처리와 ChatGPT 를 활용한 서비스 구현 — 3일 과정 실습 저장소.
**Python·패키지 설치 없이**, VSCode Dev Container 하나로 모두 동일한 환경에서 실습합니다.

> **실습 예제 정책 — 자체완결(self-contained)**
> - 모든 실습 예제(Day 1~3)가 **이 저장소 안에** 있습니다. 외부 저장소 clone 이 필요 없습니다.
> - Day 1(Pandas·정규식·sklearn), Day 2(OpenAI API·챗봇), Day 3(LangChain·RAG·Agent·MCP) 전부 `notebooks/` · `web/` · `mcp_demo/` 에서 진행합니다.
> - 각 노트북은 **그대로 실행 → 변형(TODO)** 흐름으로 구성돼 있습니다.

## 빠른 시작

### 1. 호스트 준비 (단 2개)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows 는 WSL2 기반)
- [VSCode](https://code.visualstudio.com/) + **Dev Containers** 확장
  (`ms-vscode-remote.remote-containers`)

### 2. Fork 후 내 저장소에서 clone
GitHub 에서 원본 저장소(<https://github.com/sungyong33/nlp>)를 **Fork** 한 뒤:
```bash
# <MY_ID> 를 본인 GitHub 계정으로 바꾸세요
git clone https://github.com/<MY_ID>/nlp.git
cd nlp/handson
code .
```
명령 팔레트(`Ctrl+Shift+P`) → **Dev Containers: Reopen in Container**
→ 최초 1회 이미지 빌드 + 패키지 설치 + `data/reviews.csv` 생성 (수 분 소요).

> 실습 산출물은 **내 Fork 에 commit / push** 하며 진행합니다.
> 원본 변경분 동기화: `git remote add upstream https://github.com/sungyong33/nlp.git && git pull upstream main`

### 3. API Key 넣기
- 컨테이너 생성 시 `.env.example` → `.env` 가 자동 복사됩니다.
- `.env` 의 `OPENAI_API_KEY` 를 본인 키로 채우세요. **`.env` 는 commit 금지.**

### 4. 동작 확인 (컨테이너 터미널)
```bash
python --version                                  # Python 3.11.x
python -c "import pandas, sklearn, openai; print('OK')"
python -c "import langchain, langchain_openai, faiss, mcp; print('OK')"
streamlit hello                                   # http://localhost:8501 자동 포워딩
```

## 실습 ↔ 예제 매핑 (슬라이드와 1:1)

| 실습 | 위치 | 산출물 |
|------|------|--------|
| **실습 1.** 텍스트 데이터 처리 | `notebooks/01_text_cleaning.ipynb` | `data/reviews_clean.parquet` |
| **실습 2.** 지도학습 분류 | `notebooks/02_sentiment.ipynb` | 모델 비교표 + 혼동 행렬 |
| **실습 3.** OpenAI API 활용 | `notebooks/03_openai_llm.ipynb` | 분류 셀 + ML vs LLM 비교표 |
| **실습 4.** 챗봇 (메모리) | `notebooks/04_chatbot_memory.ipynb` | 멀티턴 챗봇 + 환각 로그 |
| **실습 5.** 웹 챗봇 | `web/streamlit_app.py` + `web/gradio_app.py` | 데모 URL |
| **실습 6.** RAG + MCP | `notebooks/06_rag.ipynb` · `notebooks/07_agent_tools.ipynb` · `web/streamlit_rag.py` · `mcp_demo/library_server.py` | RAG 챗봇 + MCP 서버 |

## 이 저장소가 제공하는 파일
```
notebooks/   실습 1~6 노트북 (전부 자체완결)
  01_text_cleaning.ipynb    실습 1 — 텍스트 정제 (Pandas·정규식)
  02_sentiment.ipynb        실습 2 — sklearn 감성 분류
  03_openai_llm.ipynb       실습 3 — OpenAI API · 리뷰 분류 · 비용
  04_chatbot_memory.ipynb   실습 4 — 멀티턴 메모리 챗봇
  06_rag.ipynb              실습 6-1 — LangChain + FAISS RAG
  07_agent_tools.ipynb      실습 6-3 — Agent 도구 → MCP
data/        make_reviews.py (실습 1·2 데이터 생성기) · sample_docs/ (RAG 샘플 문서)
web/         streamlit_app.py (실습 5-1) · gradio_app.py (실습 5-2) · streamlit_rag.py (실습 6-2)
mcp_demo/    library_server.py + library_client.py — 실습 6-3 (MCP 표준 체험·자체완결)
```

## 실행 방법 요약
```bash
# 노트북 — VSCode 에서 .ipynb 열어 셀 실행 (Day 1~3)
# 웹 챗봇 (실습 5)
streamlit run web/streamlit_app.py        # 8501 포워딩
python web/gradio_app.py                   # 7860 포워딩 (share=True 로 외부 URL)
# 문서 RAG 챗봇 (실습 6)
streamlit run web/streamlit_rag.py         # 문서 업로드 → 즉시 RAG
# MCP (실습 6) — 컨테이너 안에서 완결, 외부 도구 불필요
python mcp_demo/library_client.py               # 클라이언트가 서버를 자동 실행 → 도구 호출까지 체험
python mcp_demo/library_server.py               # (선택) 서버만 단독 실행 — Codex CLI 등에 등록
```

## 컨테이너가 제공하는 것
- **Python 3.11** + 실습 패키지(`.devcontainer/requirements.txt`) — **uv**(Astral)로 설치 (pip 대비 수 배 빠름, 없으면 pip 폴백)
- VSCode 확장: Python · Jupyter · Ruff · Markdown/Mermaid · Copilot
- 포트 자동 포워딩: Streamlit `8501` · Gradio `7860` · Jupyter `8888`

## 패키지 추가
실습 중 패키지가 더 필요하면 컨테이너 터미널에서 바로:
```bash
# uv 로 시스템 Python 에 설치 (post-create.sh 와 동일 방식)
sudo env "PATH=$PATH" uv pip install --system <패키지>
# uv 가 없으면: sudo pip install <패키지>
```
영구 반영하려면 `.devcontainer/requirements.txt` 에 추가 후
**Dev Containers: Rebuild Container**.

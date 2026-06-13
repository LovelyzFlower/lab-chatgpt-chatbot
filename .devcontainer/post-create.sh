#!/usr/bin/env bash
# Dev Container 생성 직후 1회 실행되는 셋업 스크립트
set -euo pipefail

echo "==> Python 도구 점검"
python --version
uv --version 2>/dev/null && echo "    (uv 사용 가능 — 패키지 설치 가속)"

echo "==> 실습 패키지 설치 (.devcontainer/requirements.txt) — 수 분 소요"
if command -v uv >/dev/null 2>&1; then
  # uv 로 시스템 Python 에 설치 (pip 대비 수 배 빠름)
  # remoteUser=vscode 는 /usr/local/lib/.../site-packages 에 쓰기 권한이 없으므로
  # sudo 로 설치하되, uv 경로를 찾도록 현재 PATH 를 그대로 넘긴다.
  sudo env "PATH=$PATH" uv pip install --system -r .devcontainer/requirements.txt
else
  sudo pip install --upgrade pip >/dev/null
  sudo pip install -r .devcontainer/requirements.txt
fi

echo "==> 핵심 패키지 임포트 확인"
python -c "import pandas, sklearn, openai, streamlit, gradio; print('core packages OK')"
python -c "import langchain, langchain_openai, faiss, mcp; print('langchain/RAG/MCP stack OK')"

echo "==> Claude Code CLI 설치 (Node 불필요 — 공식 네이티브 설치 스크립트)"
if command -v claude >/dev/null 2>&1; then
  echo "    (이미 설치됨: $(claude --version 2>/dev/null || echo claude))"
else
  curl -fsSL https://claude.ai/install.sh | bash
  # 설치 경로(~/.local/bin)를 vscode 사용자 PATH 에 영구 등록
  if ! grep -q '/.local/bin' "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
  fi
  export PATH="$HOME/.local/bin:$PATH"
  command -v claude >/dev/null 2>&1 && echo "    (설치 완료: $(claude --version 2>/dev/null || echo claude))"
fi

echo "==> OpenAI Codex CLI 설치 (npm @openai/codex)"
if command -v codex >/dev/null 2>&1; then
  echo "    (이미 설치됨: $(codex --version 2>/dev/null || echo codex))"
elif command -v npm >/dev/null 2>&1; then
  npm install -g @openai/codex
  command -v codex >/dev/null 2>&1 && echo "    (설치 완료: $(codex --version 2>/dev/null || echo codex))"
else
  echo "    [경고] npm 을 찾을 수 없어 Codex CLI 설치를 건너뜁니다 (node feature 확인)"
fi

echo "==> Day 1 실습 데이터 생성 (data/reviews.csv)"
[ -f data/reviews.csv ] || python data/make_reviews.py

# .env 템플릿 생성 (없을 때만) — 수강생은 OPENAI_API_KEY 만 채우면 됨
if [ ! -f .env ] && [ -f .env.example ]; then
  cp .env.example .env
  echo "==> .env 생성됨 — OPENAI_API_KEY 를 본인 키로 채우세요 (.env 는 commit 금지)"
fi

echo "==> 셋업 완료. 모든 실습 예제가 이 저장소에 포함되어 있습니다."
echo "    - Day 1: notebooks/01_text_cleaning.ipynb · 02_sentiment.ipynb"
echo "    - Day 2: notebooks/03_openai_llm.ipynb · 04_chatbot_memory.ipynb"
echo "    - Day 3: notebooks/06_rag.ipynb · 07_agent_tools.ipynb · web/ · mcp_demo/"

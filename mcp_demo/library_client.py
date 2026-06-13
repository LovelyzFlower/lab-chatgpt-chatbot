"""실습 6 Task 3 — MCP 클라이언트 한 입 (컨테이너 안에서 완결).

`library_server.py` 를 stdio 로 직접 띄워 MCP 표준으로 통신한다.
**Codex CLI 등 외부 호스트 없이** 이 한 파일로 MCP 의 전 과정을 체험한다:
  1) 서버 연결 + 핸드셰이크(initialize)
  2) 서버가 제공하는 도구 목록 조회(list_tools)
  3) 도구 호출(call_tool) — search_book / loan_status
  4) 리소스 읽기(read_resource) — config://library

실행 (컨테이너 터미널):
    python mcp_demo/library_client.py

> 이것이 Codex CLI·Cursor 같은 'MCP 호스트' 가 내부적으로 하는 일과 똑같다.
> 차이는 호스트가 그 결과를 LLM 컨텍스트로 넘긴다는 점뿐.
"""
import asyncio
import sys
from pathlib import Path

from pydantic import AnyUrl

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 같은 폴더의 서버를 현재 파이썬으로 실행 (CWD 와 무관하게 동작)
SERVER = Path(__file__).resolve().parent / "library_server.py"
SERVER_PARAMS = StdioServerParameters(command=sys.executable, args=[str(SERVER)])


def _text(result) -> str:
    """call_tool 결과에서 사람이 읽을 텍스트만 뽑는다."""
    parts = []
    for item in getattr(result, "content", []) or []:
        parts.append(getattr(item, "text", str(item)))
    return "\n".join(parts) if parts else str(result)


async def main() -> None:
    print(f"==> MCP 서버 실행: {SERVER.name}\n")
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            # 1) 핸드셰이크
            info = await session.initialize()
            print(f"[1] 연결됨 — 서버: {info.serverInfo.name}\n")

            # 2) 도구 목록 — 서버의 docstring 이 LLM 이 읽는 '설명' 이 된다
            tools = await session.list_tools()
            print("[2] 제공 도구:")
            for t in tools.tools:
                print(f"    - {t.name}: {t.description}")
            print()

            # 3) 도구 호출 — LLM(또는 우리)이 인자를 채워 호출
            r1 = await session.call_tool("search_book", {"query": "해리포터"})
            print("[3] search_book('해리포터') →", _text(r1))

            r2 = await session.call_tool("loan_status", {"member_id": "M021"})
            print("    loan_status('M021')  →", _text(r2))
            print()

            # 4) 리소스 읽기
            res = await session.read_resource(AnyUrl("config://library"))
            print("[4] resource config://library →", res.contents[0].text)

    print("\n==> 완료. 같은 도구가 Codex CLI 같은 외부 호스트에서도 동일하게 보인다.")


if __name__ == "__main__":
    asyncio.run(main())

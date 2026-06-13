"""실습 6 Task 3 — MCP 서버 한 입 (표준 체험).

`07_agent_tools.ipynb` 에서 LLM 이 '도구'를 골라 쓰는 흐름을 본 뒤,
같은 도구를 MCP(Model Context Protocol) 표준으로 노출해 본다.

실행:
    python mcp_demo/library_server.py        # stdio 로 동작

OpenAI Codex CLI 등록 예 (~/.codex/config.json):
    {
      "mcpServers": {
        "library-tools": { "command": "python", "args": ["mcp_demo/library_server.py"] }
      }
    }
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("library-tools")


@mcp.tool()
def search_book(query: str) -> str:
    """제목/저자로 도서를 검색한다."""
    # 실제로는 DB/검색엔진 조회
    return f"'{query}' 검색 결과: 해리포터, 반지의 제왕, 어린 왕자"


@mcp.tool()
def loan_status(member_id: str) -> dict:
    """회원의 현재 대출 현황."""
    return {"member_id": member_id, "loans": 2, "overdue": 0}


@mcp.resource("config://library")
def get_config() -> str:
    """도서관 운영 정보(리소스)."""
    return "도서관 운영시간: 09:00~22:00"


if __name__ == "__main__":
    mcp.run()

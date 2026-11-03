from __future__ import annotations

from pathlib import Path
from typing import cast

import httpx
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel

from .config import get_settings
from .models_errors import ERROR_RESPONSES, BaseProblemError


def load_mcp_docs() -> str:
    path = Path(__file__).with_name("MCP_DOCS.md")
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "# CU LMS MCP\n\nDocumentation file `MCP_DOCS.md` is missing."


MCP_DOCS = load_mcp_docs()


def raise_for_lms_error(response: httpx.Response) -> None:
    """Parse an error body into a typed problem detail and raise ToolError."""
    if response.is_success:
        return
    try:
        payload = cast(object, response.json())
    except ValueError:
        payload = {
            "title": response.reason_phrase,
            "status": response.status_code,
        }
    model_cls = ERROR_RESPONSES.get(response.status_code, BaseProblemError)
    problem = model_cls.model_validate(payload)
    raise ToolError(problem.model_dump_json(by_alias=True, exclude_none=True))


async def get_json(
    path: str,
    *,
    params: BaseModel | None = None,
) -> dict[str, object]:
    settings = get_settings()
    query = params.model_dump(exclude_none=True) if params is not None else None
    async with httpx.AsyncClient(timeout=settings.timeout) as client:
        response = await client.get(
            f"{settings.base_url}{path}",
            headers=settings.auth_headers,
            params=query,
        )
        raise_for_lms_error(response)
        return cast(dict[str, object], response.json())

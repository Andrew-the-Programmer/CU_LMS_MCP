"""MCP server exposing read-only CU LMS endpoints."""

from __future__ import annotations

from typing import Any, TypeVar

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel

from .config import get_settings
from .models_errors import ERROR_RESPONSES, BaseProblemError
from .models_params import (
    ContentDownloadLinkParams,
    ListStudentCoursesParams,
    LongreadMaterialsParams,
)
from .models_responses import (
    CourseOverviewByIdResponse,
    CourseSummaryByIdResponse,
    CourseThemeSummaryByIdResponse,
    CurrentStudentResponse,
    GenerateContentDownloadLinkResponse,
    ListStudentCoursesResponse,
    LongreadMaterialsByIdResponse,
    LongreadSummaryByIdResponse,
    TaskByIdResponse,
)
from .models_scalars import CourseId, CourseThemeId, LongreadId, TaskId

mcp = MCPServer("CU LMS Bridge")


def _raise_for_lms_error(response: httpx.Response) -> None:
    """Parse an error body into a typed problem detail and raise ToolError."""
    if response.is_success:
        return
    try:
        payload = response.json()
    except ValueError:
        payload = {
            "title": response.reason_phrase,
            "status": response.status_code,
        }
    model_cls = ERROR_RESPONSES.get(response.status_code, BaseProblemError)
    problem = model_cls.model_validate(payload)
    raise ToolError(problem.model_dump_json(by_alias=True, exclude_none=True))


async def _get_json(
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
        _raise_for_lms_error(response)
        return response.json()


@mcp.tool()
async def get_student_profile() -> CurrentStudentResponse:
    """Get the currently authenticated student (GET /micro-lms/students/me)."""
    return CurrentStudentResponse.model_validate(
        await _get_json("/students/me")
    )


@mcp.tool()
async def list_student_courses(
    params: ListStudentCoursesParams | None = None,
) -> ListStudentCoursesResponse:
    """List courses the student is enrolled in (GET /micro-lms/courses/student)."""
    return ListStudentCoursesResponse.model_validate(
        await _get_json("/courses/student", params=params)
    )


@mcp.tool()
async def get_course_summary(course_id: CourseId) -> CourseSummaryByIdResponse:
    """Get a course summary by ID (GET /micro-lms/courses/{courseId})."""
    return CourseSummaryByIdResponse.model_validate(
        await _get_json(f"/courses/{course_id}")
    )


@mcp.tool()
async def get_course_overview(
    course_id: CourseId,
) -> CourseOverviewByIdResponse:
    """Get a course overview (themes + longreads) by ID.

    Corresponds to GET /micro-lms/courses/{courseId}/overview.
    """
    return CourseOverviewByIdResponse.model_validate(
        await _get_json(f"/courses/{course_id}/overview")
    )


@mcp.tool()
async def get_course_theme_summary(
    theme_id: CourseThemeId,
) -> CourseThemeSummaryByIdResponse:
    """Get a course theme summary by ID (GET /micro-lms/themes/{themeId})."""
    return CourseThemeSummaryByIdResponse.model_validate(
        await _get_json(f"/themes/{theme_id}")
    )


@mcp.tool()
async def get_longread_summary(
    longread_id: LongreadId,
) -> LongreadSummaryByIdResponse:
    """Get a longread summary by ID (GET /micro-lms/longreads/{longreadId})."""
    return LongreadSummaryByIdResponse.model_validate(
        await _get_json(f"/longreads/{longread_id}")
    )


@mcp.tool()
async def get_longread_materials(
    longread_id: LongreadId,
    params: LongreadMaterialsParams | None = None,
) -> LongreadMaterialsByIdResponse:
    """Get longread materials/blocks by ID.

    Corresponds to GET /micro-lms/longreads/{longreadId}/materials.
    """
    return LongreadMaterialsByIdResponse.model_validate(
        await _get_json(
            f"/longreads/{longread_id}/materials",
            params=params,
        )
    )


@mcp.tool()
async def get_task(task_id: TaskId) -> TaskByIdResponse:
    """Get a task by ID (GET /micro-lms/tasks/{taskId})."""
    return TaskByIdResponse.model_validate(await _get_json(f"/tasks/{task_id}"))


@mcp.tool()
async def generate_content_download_link(
    params: ContentDownloadLinkParams,
) -> GenerateContentDownloadLinkResponse:
    """Generate a content download link (GET /micro-lms/content/download-link)."""
    return GenerateContentDownloadLinkResponse.model_validate(
        await _get_json("/content/download-link", params=params)
    )


def main() -> None:
    _ = get_settings()  # fail fast
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

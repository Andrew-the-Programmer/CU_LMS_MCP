"""MCP server exposing read-only CU LMS endpoints."""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from . import utils
from .config import get_settings
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


@mcp.tool()
async def get_lms_guide() -> str:
    """Return the CU LMS usage guide (read-only).

    Call this first when you need to map a student's wording to API
    concepts: `theme` is a week, `longread` is an unnamed block container,
    `coding` is homework, and `questions` is a test. The guide also explains
    late days, ID rules, and the typical tool workflow.

    Returns:
        str: Markdown guide loaded from `MCP_DOCS.md` at server startup.
    """
    return utils.MCP_DOCS


@mcp.tool()
async def get_student_profile() -> CurrentStudentResponse:
    """Return the authenticated student's LMS profile (read-only).

    Use this when the student asks "who am I", "my profile", or needs their
    name, email, study level, or late-days balance.

    Returns:
        CurrentStudentResponse: student identity and study metadata.
    """
    return CurrentStudentResponse.model_validate(
        await utils.get_json("/students/me")
    )


@mcp.tool()
async def list_student_courses(
    params: ListStudentCoursesParams | None = None,
) -> ListStudentCoursesResponse:
    """List the courses the student is enrolled in (read-only).

    Students usually ask for "my courses" or "what courses do I have".
    Results are paginated: `limit` defaults to 25, `offset` skips items, and
    `state` filters by publication state. Omit `params` to use defaults.

    Returns:
        ListStudentCoursesResponse: `items` plus `paging` metadata.
    """
    return ListStudentCoursesResponse.model_validate(
        await utils.get_json("/courses/student", params=params)
    )


@mcp.tool()
async def get_course_summary(course_id: CourseId) -> CourseSummaryByIdResponse:
    """Return one course's summary by `course_id` (read-only).

    Use this after `list_student_courses` when the student asks about a
    specific course, its settings, category, or publication state.

    Parameters:
        course_id: Course ID from `list_student_courses`.

    Returns:
        CourseSummaryByIdResponse: course metadata and settings.
    """
    return CourseSummaryByIdResponse.model_validate(
        await utils.get_json(f"/courses/{course_id}")
    )


@mcp.tool()
async def get_course_overview(
    course_id: CourseId,
) -> CourseOverviewByIdResponse:
    """Return a course's structure: weeks and their sections (read-only).

    Start here after choosing a course. In the LMS UI a `theme` is a week
    ("Неделя 1", "Неделя 2"). Each theme contains one or more `longreads`;
    a longread is an unnamed container inside a week and is not shown to
    students by that name. A longread holds materials, homework, a test, or
    another block.

    Use the returned `theme.id` with `get_course_theme_summary`, and the
    `longread.id` with `get_longread_summary` or `get_longread_materials`.

    Parameters:
        course_id: Course ID from `list_student_courses`.

    Returns:
        CourseOverviewByIdResponse: themes (weeks) with nested longreads.
    """
    return CourseOverviewByIdResponse.model_validate(
        await utils.get_json(f"/courses/{course_id}/overview")
    )


@mcp.tool()
async def get_course_theme_summary(
    theme_id: CourseThemeId,
) -> CourseThemeSummaryByIdResponse:
    """Return one week's summary by `theme_id` (read-only).

    A `theme` is a week in the LMS UI. Use this when the student asks what
    is in a specific week; the response lists the week's sections
    (longreads). Get `theme_id` from `get_course_overview`.

    Parameters:
        theme_id: Theme (week) ID.

    Returns:
        CourseThemeSummaryByIdResponse: week metadata and sections.
    """
    return CourseThemeSummaryByIdResponse.model_validate(
        await utils.get_json(f"/themes/{theme_id}")
    )


@mcp.tool()
async def get_longread_summary(
    longread_id: LongreadId,
) -> LongreadSummaryByIdResponse:
    """Return one week section by `longread_id` (read-only).

    A `longread` is an unnamed container inside a week; the LMS UI does not
    show that term. Use this to inspect a section before listing its
    materials. Get `longread_id` from `get_course_overview` or
    `get_course_theme_summary`.

    Parameters:
        longread_id: Longread/section ID.

    Returns:
        LongreadSummaryByIdResponse: section metadata.
    """
    return LongreadSummaryByIdResponse.model_validate(
        await utils.get_json(f"/longreads/{longread_id}")
    )


@mcp.tool()
async def get_longread_materials(
    longread_id: LongreadId,
    params: LongreadMaterialsParams | None = None,
) -> LongreadMaterialsByIdResponse:
    """Return the blocks inside a week section (read-only).

    A longread is an unnamed container inside a week. Its items are blocks:

    - `markdown`, `file`, `image`, `video`, `audio`: learning materials,
      usually files or media;
    - `coding`: homework/ДЗ, usually a description plus files;
    - `questions`: a test/quiz, usually questions without files.

    Only `coding` and `questions` items expose `task_id`. To open homework
    or a test, call `get_task(item.task_id)`, not `get_task(item.id)`.

    Results are paginated with `limit` (default 25) and `offset`.

    Parameters:
        longread_id: Longread/section ID from the course overview or theme
            summary.
        params: Optional pagination (`limit`, `offset`).

    Returns:
        LongreadMaterialsByIdResponse: `items` plus `paging` metadata.
    """
    return LongreadMaterialsByIdResponse.model_validate(
        await utils.get_json(
            f"/longreads/{longread_id}/materials",
            params=params,
        )
    )


@mcp.tool()
async def get_task(task_id: TaskId) -> TaskByIdResponse:
    """Return a homework or test by `task_id` (read-only).

    Use this only for `coding` (homework/ДЗ) or `questions` (test) blocks.
    Take `task_id` from `item.task_id`; `item.id` is the material ID and will
    not work here. The response contains the task state, score, exercise
    settings, and solution/answers when available.

    Parameters:
        task_id: Task ID from `item.task_id`.

    Returns:
        TaskByIdResponse: task state, score, exercise, and solution.
    """
    return TaskByIdResponse.model_validate(
        await utils.get_json(f"/tasks/{task_id}")
    )


@mcp.tool()
async def generate_content_download_link(
    params: ContentDownloadLinkParams,
) -> GenerateContentDownloadLinkResponse:
    """Create a download URL for a file stored in LMS (read-only).

    Use this when the student asks to download a file or material. Pass the
    storage `filename` from a file/image/video/audio material. `version` is
    optional and must be the 8-character hex revision from that material
    when present.

    The API returns a link even for a nonexistent filename; verify that the
    material came from the LMS before sharing the URL.

    Parameters:
        params: `filename` (required storage path) and optional `version`.

    Returns:
        GenerateContentDownloadLinkResponse: a downloadable URL.
    """
    return GenerateContentDownloadLinkResponse.model_validate(
        await utils.get_json("/content/download-link", params=params)
    )


def main() -> None:
    _ = get_settings()  # fail fast
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

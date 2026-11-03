import logging
from typing import cast

import pytest

from cu_lms_mcp import server
from cu_lms_mcp.models_params import (
    ContentDownloadLinkParams,
    ListStudentCoursesParams,
    LongreadMaterialsParams,
)
from cu_lms_mcp.models_responses import (
    CourseSummaryItem,
    CourseThemeItem,
    LongreadItem,
    LongreadMaterialItem,
)
from cu_lms_mcp.models_scalars import TaskId

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_get_student_profile():
    _ = await server.get_student_profile()


async def t_course(course: CourseSummaryItem) -> None:
    logger.info("%s", course.name)

    _ = await server.get_course_summary(course.id)
    overview = await server.get_course_overview(course.id)

    for theme in overview.themes:
        await t_course_theme(theme)


async def t_course_theme(theme: CourseThemeItem) -> None:
    logger.info("%s", theme.name)

    _ = await server.get_course_theme_summary(theme.id)

    for longread in theme.longreads:
        await t_longread(longread)


async def t_longread(longread: LongreadItem) -> None:
    logger.info("%s", longread.name)
    _ = await server.get_longread_summary(longread.id)
    materials = await server.get_longread_materials(
        longread.id, LongreadMaterialsParams(limit=1)
    )

    for item in materials.items:
        await t_material(item)


async def t_material(item: LongreadMaterialItem) -> None:
    logger.info("%s", type(item))

    if hasattr(item, "filename"):
        filename = cast(str, getattr(item, "filename"))
        res = await server.generate_content_download_link(
            ContentDownloadLinkParams(filename=filename)
        )
        logger.info("Att download link: %s", res.url)

    task_id = cast(TaskId | None, getattr(item, "task_id", None))
    if task_id is not None:
        task = await server.get_task(task_id)
        logger.info("Task: %s", task.type)


@pytest.mark.asyncio
async def test_all_tools():
    courses = await server.list_student_courses(
        ListStudentCoursesParams(limit=1)
    )
    assert courses.items, "no courses returned"

    logger.info("Courses count: %s", len(courses.items))

    for course in courses.items:
        await t_course(course)

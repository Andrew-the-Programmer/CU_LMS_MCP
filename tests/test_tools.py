import pytest

from cu_lms_mcp import server


@pytest.mark.asyncio
async def test_get_student_profile():
    _ = await server.get_student_profile()


@pytest.mark.asyncio
async def test_all_tools():
    courses = await server.list_student_courses()
    assert courses.items, "no courses returned"

    for course in courses.items:
        print(f"Course: {course.name}")

        _ = await server.get_course_overview(course.id)
        _ = await server.get_course_summary(course.id)
        overview = await server.get_course_overview(course.id)

        for theme in overview.themes:
            print(f"\tTheme: {theme.name}")

            _ = await server.get_course_theme_summary(theme.id)

            for longread in theme.longreads:
                print(f"\t\tLongread: {longread.name}")

                _ = await server.get_longread_summary(longread.id)
                materials = await server.get_longread_materials(longread.id)

                for item in materials.items:
                    print(f"\t\t\tItem: {item.id}")
                    # kind = (getattr(item, "type", None) or "").lower()
                    # if kind in {"exercise", "test", "task"}:
                    task = await server.get_task(item.id)
                    print(f"\t\t\t\tTask: {task.type}")

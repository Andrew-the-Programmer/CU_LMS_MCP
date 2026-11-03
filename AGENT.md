# AGENT.md

Repository guidance for coding agents working on the CU LMS MCP server. Read
`README.md` first for setup and user-facing usage.

## Scope

This repository is a read-only MCP server for the Central University LMS API.
Do not add write operations (submissions, edits, deletes) unless explicitly
requested and verified against the API specification.

## Commands

```bash
poetry install
poetry run python -m cu_lms_mcp.server
poetry run black .
poetry run isort .
poetry run basedpyright
```

Tests hit the live LMS API and require `.env`:

```bash
poetry run pytest
poetry run pytest -v -s --log-cli-level=INFO
```

The maintainer runs the live suite. Do not run `pytest` after editing tests
unless explicitly asked.

## Architecture

```text
cu_lms_mcp/
  server.py            MCP server and @mcp.tool definitions
  utils.py             HTTP helper and MCP docs loader
  config.py            pydantic-settings config and auth headers
  models_params.py     query-argument models and query scalar aliases
  models_responses.py  response models, CuBaseModel, material union
  models_errors.py     problem-detail models and status mapping
  models_scalars.py    shared scalar aliases
  MCP_DOCS.md          agent-facing guide returned by get_lms_guide
tests/test_tools.py    live smoke walk
api_docs.yaml          OpenAPI specification snapshot
```

`server.py` contains only the MCP server and tool functions; it imports
`utils` and calls `utils.foo()`. Active non-tool helpers live in `utils.py`;
the parked composite-tool helpers are at the end of this file.

All HTTP goes through `utils.get_json`:

```python
async def get_json(
    path: str,
    *,
    params: BaseModel | None = None,
) -> dict[str, object]:
```

It builds query parameters with `model_dump(exclude_none=True)`, sends the
cookie header, maps error responses, and returns decoded JSON.

## LMS/API vocabulary

The API names do not match the student-facing LMS UI:

- `CourseTheme` (`theme`, `CourseThemeItem`, `/themes/{themeId}`) is a
  **week** in the UI: "Неделя 1", "Неделя 2", etc.
- `Longread` (`longread`, `LongreadItem`, `/longreads/{longreadId}`) is an
  unnamed container inside a week. The UI does not use the word "longread"
  and may not display `LongreadItem.name`. A week usually contains one or
  more blocks such as materials, homework, or a test.
- `LongreadMaterialItem` is a block inside a longread:
  - `markdown`, `file`, `image`, `video`, `audio`, `videoPlatform`:
    learning materials; usually files/media or text.
  - `coding`: homework/ДЗ; usually a description plus files; has a nullable
    `task_id`.
  - `questions`: test/quiz; questions and options, usually no files; has a
    nullable `task_id`.
- `Task` (`TaskByIdResponse`, `/tasks/{taskId}`) is the graded entity behind
  a `coding` or `questions` material. Call `get_task(material.task_id)`;
  `material.id` is not a task ID.

Use API terms (`theme`, `longread`, `material`, `task`) in code, models,
tests, and this file. Use student terms ("неделя", "материалы", "ДЗ", "тест")
in `README.md` and other user-facing text. Do not expose `longread` as a
student-facing concept.

## Tool conventions

- Path IDs are separate named parameters typed with aliases from
  `models_scalars.py`: `course_id: CourseId`, `theme_id: CourseThemeId`,
  `longread_id: LongreadId`, `task_id: TaskId`. Do not use bare `int`.
- Query-string arguments go into a single params model from
  `models_params.py`. Do not embed path IDs in that model. Local search terms
  (`resolve_course(query=...)`, `resolve_week(week=...)`) stay as separate
  semantic parameters; they are not HTTP query arguments.
- Optional params use `params: SomeParams | None = None`; required params stay
  required. `generate_content_download_link` is required because `filename` is
  required.
- `utils.get_json` accepts only `path` and `params`; never add exclude lists or
  path-ID filtering.
- Tool functions are `async`, return a Pydantic response model, and call
  `Model.model_validate(await utils.get_json(...))`.
- The server uses stdio transport through `mcp.run(transport="stdio")`.
- MCP clients never see `AGENT.md` or `README.md`. All agent-facing guidance
  must be in tool docstrings, `get_lms_guide`, or server metadata.
- Every tool docstring must contain: what it returns and that it is read-only;
  when to call it in student terms; a `Parameters:` block with the source of
  each ID; a `Returns:` block; and the next tool in the chain.

## Parked composite tools

`get_lms_guide` is live and returns `MCP_DOCS.md`, loaded once in `utils.py`
with `Path(__file__).with_name("MCP_DOCS.md")`. Keep the file in the package
and included in the wheel via `pyproject.toml`.

The other composite tools — `resolve_course`, `resolve_week`,
`get_week_contents`, `list_homework`, `list_tests` — were removed from the
server. Their implementation and helpers are parked at the end of this file
for future work; they are not registered with `mcp` and not covered by tests.

## Late days (LD / ЛД)

- `CurrentStudentResponse.late_days_balance` is the remaining balance. Students
  receive about 50 at the start of the semester.
- `TaskByIdResponse.late_days` is the number **already spent**, not the
  remaining balance.
- `is_late_days_enabled` on the material activity or task says whether the
  activity allows extensions.
- Only `coding` materials (homework/ДЗ) can be extended. `questions`
  materials (tests/quizzes/КР) cannot.
- A task cannot be extended if a solution is already attached. Check
  `TaskSolution.attachments`, `TaskSolution.answers`, and
  `TaskSolution.solution_url`.
- One late day extends the deadline by one day. Example: Monday 22:00 + 1 LD =
  Tuesday 22:00.
- The parked `list_homework` implementation computes `late_days_available`,
  `late_days_needed`, and `extended_deadline`. It uses the task when
  `task_id` is present; otherwise it falls back to the material activity flag
  and the profile balance.

## Model conventions

- `CuBaseModel` in `models_responses.py` sets:
  - `alias_generator=to_camel`
  - `populate_by_name=True`
  - `extra="forbid"`
- Keep `extra="forbid"`. When the live API returns a field missing from
  `api_docs.yaml`, declare it explicitly in the model. Do not switch to
  `extra="allow"` or `extra="ignore"` to silence validation failures. Error
  models in `models_errors.py` use `extra="allow"` because problem payloads
  vary by status.
- Put response models in `models_responses.py`, query params in
  `models_params.py`, shared scalars in `models_scalars.py`, and error bodies
  in `models_errors.py`.
- Prefer existing scalar aliases (`CourseId`, `TaskId`, `PublishDate`,
  `LongreadMaterialVersion`, etc.) over raw `int`/`str`/`datetime` in new
  fields. One exception: `CourseSkillLevel` in `models_scalars.py` is still
  `Literal["none"]` and is unused by `CourseSettings.skill_level`, which is
  deliberately `str` because live data can contain `intermediate`.
- Preserve nullable fields that are required by the API: a field can be
  required and still accept `None` (`field: T | None` without a default).
- `LongreadMaterialItem` is a discriminated union on `discriminator`. A
  material block is not a task: `item.id` is the material ID. Only the
  `coding` and `questions` items expose `item.task_id` (nullable); other
  material types do not have a task ID.

## Known live-API divergences

The live API is not fully consistent with `api_docs.yaml`. Current known
differences, which are represented in the models:

- `CourseSettings.skillLevel` is typed `str`; the spec enum lists only `none`,
  but live data can contain `intermediate`.
- `CourseSummaryItem.categoryCover` can be `null`; the spec marks it required
  and non-null.
- Course payloads include `participationType`, `commitLevel`, and `blocker`
  fields absent from the spec. `blocker` has `{enabled, enableAt, score}`.
- Course overview responses can include `blocker`.
- `LongreadMaterialActivity` includes `bestScoresCount`.
- Coding materials and task exercises include `isCodeEditorEnabled`.
- Coding/questions material `taskId` can be `null`.
- Questions material `mode` and `questions` can be `null`.
- `TaskExercise.timer` and `TaskExercise.mode` can be non-null even though the
  spec marks them only-null.
- `TaskSolutionAnswersItem.answer` can be a list of option IDs for
  multiple-choice questions, not only `str | number`.

Re-verify against live responses before changing these; API behavior can
change.

## Adding a tool

1. Add or reuse response models in `models_responses.py`.
2. Add query params to `models_params.py` if needed.
3. Use an existing scalar alias from `models_scalars.py` for path IDs.
4. Define the tool in `server.py` with `@mcp.tool()`.
5. Build the path from the named ID and pass only `params=...` to
   `utils.get_json`.
6. Add focused coverage in a new `tests/test_*.py` module. Keep
   `tests/test_tools.py` as the live smoke walk unless the task is
   specifically to extend that walk.

## Testing conventions

- `tests/test_tools.py` is a live end-to-end smoke walk, not a mocked unit
  suite.
- Keep one async helper per nesting level: `t_course`, `t_course_theme`,
  `t_longread`, `t_material`. `test_all_tools` fetches up to one course
  (`limit=1`), asserts it is non-empty, and delegates to `t_course`.
- Do not inline loops that duplicate a helper, and call each endpoint once per
  level.
- Use module-level `logger = logging.getLogger(__name__)` and `logger.info`.
  Do not add `print`, `logging.basicConfig`, or custom handlers to make logs
  appear.
- Logs are flat; there is no indentation or level parameter in the smoke walk.
- Live logging is off by default (`log_cli = false` in `pyproject.toml`). Use
  `--log-cli-level=INFO` to stream logs; `-s` alone only disables capture.
- Keep `asyncio_default_fixture_loop_scope = "function"` in pytest config to
  match the function-scoped async fixtures and avoid the pytest-asyncio
  deprecation warning.
- The parked composite tools are not registered and are not covered by
  `tests/test_tools.py`.

## Style

- Black, line length 80.
- isort with the `black` profile.
- Keep imports grouped and alphabetical within the project sections.
- Avoid comments unless they explain a non-obvious constraint or live-API
  quirk.

## Security

- `.env` contains a live session cookie and is git-ignored.
- Never print, log, commit, or expose `CU_LMS_SESSION_COOKIE`.
- Do not add write requests or destructive operations.
- Generated download links may be pre-signed; treat them as sensitive.

## Parked composite tools

These tools were removed from the live server and are kept here for
reference. They are not registered with `mcp`. Their params/response models
were also removed from `models_params.py` and `models_responses.py`, so the
code below is an archive, not a runnable module.

### Tools

```python
@mcp.tool()
async def resolve_course(
    query: str,
    params: ResolveCourseParams | None = None,
) -> ResolveCourseResponse:
    """Find courses by name for a student request (read-only).

    Use this when the student names a course instead of providing a
    `course_id` ("my math course", "Основы программирования"). It searches
    the student's course list locally and returns the best matches with their
    IDs. Use the chosen `id` with the other course tools.

    Parameters:
        query: Course name or part of it.
        params: Optional result limit and archived-course filter.

    Returns:
        ResolveCourseResponse: matching courses with `matchScore`.
    """
    params = params or ResolveCourseParams()
    needle = query.strip().casefold()
    if not needle:
        raise ToolError("query must not be empty")

    courses = [
        course
        for course in await utils.load_courses()
        if params.include_archived or not course.is_archived
    ]
    scored: list[tuple[float, CourseSummaryItem]] = []
    for course in courses:
        name = course.name.casefold()
        score = (
            1.0
            if needle in name
            else SequenceMatcher(None, needle, name).ratio()
        )
        scored.append((score, course))
    scored.sort(key=lambda pair: (-pair[0], pair[1].name.casefold()))

    return ResolveCourseResponse(
        query=query,
        items=[
            CourseMatch(
                id=course.id,
                name=course.name,
                state=course.state,
                category=course.category,
                is_archived=course.is_archived,
                match_score=round(score, 3),
            )
            for score, course in scored[: params.limit]
        ],
        total_count=len(courses),
    )


@mcp.tool()
async def resolve_week(
    course_id: CourseId,
    week: str,
) -> ResolveWeekResponse:
    """Resolve a student's week reference to a theme ID (read-only).

    Students say "Неделя 3" or "week 3"; the API calls it a `theme`. Use this
    after `resolve_course` when the student refers to a week by number or
    name. Pass the returned `theme.id` to `get_week_contents` or
    `get_course_theme_summary`.

    Parameters:
        course_id: Course ID from `list_student_courses` or `resolve_course`.
        week: Week number, theme ID, or part of the week name.

    Returns:
        ResolveWeekResponse: best `theme` match and up to 10 candidates.
    """
    overview = await get_course_overview(course_id)
    needle = week.strip().casefold()
    if not needle:
        raise ToolError("week must not be empty")

    digits = "".join(character for character in needle if character.isdigit())
    scored: list[tuple[int, float, CourseThemeItem]] = []
    for theme in overview.themes:
        exact = 0
        if str(theme.id) == needle or str(theme.order) == needle:
            exact = 2
        elif needle in theme.name.casefold():
            exact = 1
        if digits and int(digits) == theme.order:
            exact = max(exact, 2)
        ratio = SequenceMatcher(None, needle, theme.name.casefold()).ratio()
        scored.append((exact, ratio, theme))
    scored.sort(key=lambda row: (-row[0], -row[1], row[2].order))

    candidates = [
        WeekMatch(
            id=theme.id,
            name=theme.name,
            order=theme.order,
            state=theme.state,
        )
        for _, _, theme in scored[:10]
    ]
    best = scored[0] if scored else None
    theme_match = (
        candidates[0]
        if best is not None and (best[0] > 0 or best[1] >= 0.5)
        else None
    )
    return ResolveWeekResponse(
        course_id=course_id,
        query=week,
        theme=theme_match,
        candidates=candidates,
    )


@mcp.tool()
async def get_week_contents(
    course_id: CourseId,
    theme_id: CourseThemeId,
    params: WeekContentsParams | None = None,
) -> WeekContentsResponse:
    """Return everything in one week (read-only).

    A `theme` is a week in the LMS UI. Use this for "what is on week 3?".
    The response contains the week metadata plus each section (longread) and
    a short summary of its materials. Set `includeMaterials=False` to skip
    material calls, and `materialsLimit` to cap items per section.

    Parameters:
        course_id: Course ID from `list_student_courses` or `resolve_course`.
        theme_id: Week ID from `resolve_week` or `get_course_overview`.
        params: Optional `include_materials` and `materials_limit`.

    Returns:
        WeekContentsResponse: week metadata and section summaries.
    """
    params = params or WeekContentsParams()
    overview = await get_course_overview(course_id)
    theme = next(
        (item for item in overview.themes if item.id == theme_id),
        None,
    )
    if theme is None:
        raise ToolError(f"theme {theme_id} not found in course {course_id}")

    sections: list[WeekSectionSummary] = []
    for index, longread in enumerate(theme.longreads):
        materials: list[MaterialSummary] | None = None
        total_count: int | None = None
        if params.include_materials:
            page = LongreadMaterialsByIdResponse.model_validate(
                await utils.get_json(
                    f"/longreads/{longread.id}/materials",
                    params=LongreadMaterialsParams(
                        limit=params.materials_limit,
                        offset=0,
                    ),
                )
            )
            materials = [utils.material_summary(item) for item in page.items]
            total_count = page.paging.total_count
        sections.append(
            WeekSectionSummary(
                id=longread.id,
                name=longread.name,
                order=index,
                state=longread.state,
                total_count=total_count,
                materials=materials,
            )
        )

    return WeekContentsResponse(
        course_id=overview.id,
        course_name=overview.name,
        theme=WeekMatch(
            id=theme.id,
            name=theme.name,
            order=theme.order,
            state=theme.state,
        ),
        sections=sections,
    )


@mcp.tool()
async def list_homework(
    params: ListHomeworkParams | None = None,
) -> ListHomeworkResponse:
    """List homework with deadlines and late-day status (read-only).

    Students ask "what homework do I have?", "what is overdue?", or "can I
    still use late days?". This walks the student's courses, finds `coding`
    blocks (homework/ДЗ), and fetches each task. Tests and quizzes are not
    included.

    Late days: about 50 per semester; one late day extends an eligible
    homework deadline by one day. Not every homework can be extended, and a
    task with an attached solution cannot be extended. The response exposes
    `lateDaysAvailable`, `lateDaysNeeded`, and `extendedDeadline`.
    `lateDaysSpent` is already spent, not the remaining balance.

    Parameters:
        params: Optional filters by course, passed deadline, late-day
            availability, task state, title; plus pagination and archived
            courses. Omitting `course_id` scans all active courses and can be
            slow.

    Returns:
        ListHomeworkResponse: homework items and the remaining late-day
        balance.
    """
    params = params or ListHomeworkParams()
    profile = await get_student_profile()
    items: list[HomeworkItem] = []

    for _, overview in await utils.course_pairs(
        params.course_id,
        params.include_archived,
    ):
        for theme in overview.themes:
            for longread in theme.longreads:
                for material in await utils.load_materials(longread.id):
                    if not isinstance(
                        material,
                        LongreadExerciseCodingMaterialItem,
                    ):
                        continue

                    task = await utils.get_task_or_none(material.task_id)

                    deadline = (
                        task.deadline
                        if task is not None
                        else material.estimation.deadline
                    )
                    solution = (
                        utils.solution_attached(task)
                        if task is not None
                        else None
                    )
                    late_days_enabled = (
                        task.is_late_days_enabled
                        if task is not None
                        else utils.material_late_days_enabled(material)
                    )
                    balance = (
                        task.student.late_days_balance
                        if task is not None
                        else profile.late_days_balance
                    )
                    available = (
                        late_days_enabled and solution is False and balance > 0
                    )
                    needed = utils.late_days_needed(deadline)
                    extended = (
                        deadline + timedelta(days=needed)
                        if available
                        and deadline is not None
                        and needed is not None
                        and needed > 0
                        and needed <= balance
                        else None
                    )

                    item = HomeworkItem(
                        course_id=overview.id,
                        course_name=overview.name,
                        theme_id=theme.id,
                        theme_name=theme.name,
                        longread_id=longread.id,
                        longread_name=longread.name,
                        material_id=material.id,
                        title=utils.material_title(material),
                        task_id=material.task_id,
                        deadline=deadline,
                        deadline_passed=utils.deadline_passed(deadline),
                        state=task.state if task is not None else None,
                        score=task.score if task is not None else None,
                        late_days_enabled=late_days_enabled,
                        late_days_balance=balance,
                        late_days_spent=(
                            task.late_days if task is not None else None
                        ),
                        solution_attached=solution,
                        late_days_available=available,
                        late_days_needed=needed,
                        extended_deadline=extended,
                    )
                    if utils.matches_homework(item, params):
                        items.append(item)

    items.sort(
        key=lambda item: (
            item.deadline is None,
            item.deadline.timestamp() if item.deadline else 0,
            item.course_name,
            item.theme_name,
            item.longread_name,
            item.title,
        )
    )
    return ListHomeworkResponse(
        items=items[params.offset : params.offset + params.limit],
        total_count=len(items),
        late_days_balance=profile.late_days_balance,
    )


@mcp.tool()
async def list_tests(
    params: ListTestsParams | None = None,
) -> ListTestsResponse:
    """List tests and quizzes with deadlines and states (read-only).

    Students ask "what tests do I have?" or "what is overdue?". This walks
    the student's courses and finds `questions` blocks (tests/КР). Late days
    do not apply to tests. Use `get_task(item.task_id)` for full task
    details.

    Parameters:
        params: Optional filters by course, passed deadline, task state,
            title; plus pagination and archived courses. Omitting `course_id`
            scans all active courses and can be slow.

    Returns:
        ListTestsResponse: test items with task IDs and deadlines.
    """
    params = params or ListTestsParams()
    items: list[TestItem] = []

    for _, overview in await utils.course_pairs(
        params.course_id,
        params.include_archived,
    ):
        for theme in overview.themes:
            for longread in theme.longreads:
                for material in await utils.load_materials(longread.id):
                    if not isinstance(
                        material,
                        LongreadExerciseQuestionsMaterialItem,
                    ):
                        continue

                    task = await utils.get_task_or_none(material.task_id)

                    deadline = (
                        task.deadline
                        if task is not None
                        else material.estimation.deadline
                    )
                    question_count = (
                        len(material.questions)
                        if material.questions is not None
                        else (
                            len(task.exercise.question_orders)
                            if task is not None
                            and task.exercise.question_orders is not None
                            else None
                        )
                    )
                    item = TestItem(
                        course_id=overview.id,
                        course_name=overview.name,
                        theme_id=theme.id,
                        theme_name=theme.name,
                        longread_id=longread.id,
                        longread_name=longread.name,
                        material_id=material.id,
                        title=utils.material_title(material),
                        task_id=material.task_id,
                        deadline=deadline,
                        deadline_passed=utils.deadline_passed(deadline),
                        state=task.state if task is not None else None,
                        score=task.score if task is not None else None,
                        solution_attached=(
                            utils.solution_attached(task)
                            if task is not None
                            else None
                        ),
                        question_count=question_count,
                    )
                    if utils.matches_test(item, params):
                        items.append(item)

    items.sort(
        key=lambda item: (
            item.deadline is None,
            item.deadline.timestamp() if item.deadline else 0,
            item.course_name,
            item.theme_name,
            item.longread_name,
            item.title,
        )
    )
    return ListTestsResponse(
        items=items[params.offset : params.offset + params.limit],
        total_count=len(items),
    )
```

### Utils

```python
async def load_courses() -> list[CourseSummaryItem]:
    items: list[CourseSummaryItem] = []
    offset = 0
    while True:
        page = ListStudentCoursesResponse.model_validate(
            await get_json(
                "/courses/student",
                params=ListStudentCoursesParams(limit=100, offset=offset),
            )
        )
        items.extend(page.items)
        offset += len(page.items)
        if not page.items or offset >= page.paging.total_count:
            break
    return items


async def load_materials(
    longread_id: LongreadId,
) -> list[LongreadMaterialItem]:
    items: list[LongreadMaterialItem] = []
    offset = 0
    while True:
        page = LongreadMaterialsByIdResponse.model_validate(
            await get_json(
                f"/longreads/{longread_id}/materials",
                params=LongreadMaterialsParams(limit=100, offset=offset),
            )
        )
        items.extend(page.items)
        offset += len(page.items)
        if not page.items or offset >= page.paging.total_count:
            break
    return items


async def course_pairs(
    course_id: CourseId | None,
    include_archived: bool,
) -> list[tuple[CourseSummaryItem, CourseOverviewByIdResponse]]:
    if course_id is not None:
        course = CourseSummaryByIdResponse.model_validate(
            await get_json(f"/courses/{course_id}")
        )
        overview = CourseOverviewByIdResponse.model_validate(
            await get_json(f"/courses/{course_id}/overview")
        )
        return [(course, overview)]

    pairs: list[tuple[CourseSummaryItem, CourseOverviewByIdResponse]] = []
    for course in await load_courses():
        if course.is_archived and not include_archived:
            continue
        overview = CourseOverviewByIdResponse.model_validate(
            await get_json(f"/courses/{course.id}/overview")
        )
        pairs.append((course, overview))
    return pairs


def material_title(item: LongreadMaterialItem) -> str:
    name = cast(str | None, getattr(item, "name", None))
    if name:
        return name
    filename = cast(str | None, getattr(item, "filename", None))
    if filename:
        return Path(filename).name
    return f"{item.type} {item.id}"


def material_summary(item: LongreadMaterialItem) -> MaterialSummary:
    estimation = cast(
        LongreadMaterialEstimation | None,
        getattr(item, "estimation", None),
    )
    activity = estimation.activity if estimation is not None else None
    return MaterialSummary(
        id=item.id,
        kind=item.discriminator,
        type=item.type,
        name=cast(str | None, getattr(item, "name", None)),
        task_id=cast(TaskId | None, getattr(item, "task_id", None)),
        deadline=estimation.deadline if estimation is not None else None,
        is_late_days_enabled=(
            activity.is_late_days_enabled if activity is not None else None
        ),
        has_files=bool(
            cast(str | None, getattr(item, "filename", None))
            or cast(list[object] | None, getattr(item, "attachments", None))
        ),
    )


def deadline_passed(deadline: datetime | None) -> bool | None:
    if deadline is None:
        return None
    now = datetime.now(deadline.tzinfo)
    return deadline < now


def late_days_needed(deadline: datetime | None) -> int | None:
    if deadline is None:
        return None
    now = datetime.now(deadline.tzinfo)
    if now <= deadline:
        return 0
    return math.ceil((now - deadline).total_seconds() / 86400)


def solution_attached(task: TaskByIdResponse) -> bool:
    solution = task.solution
    if solution is None:
        return False
    return bool(
        solution.solution_url or solution.answers or solution.attachments
    )


async def get_task_or_none(
    task_id: TaskId | None,
) -> TaskByIdResponse | None:
    if task_id is None:
        return None
    try:
        payload = await get_json(f"/tasks/{task_id}")
    except ToolError as exc:
        exc.args
        if '"status":404' not in str(exc):
            raise
        return None
    return TaskByIdResponse.model_validate(payload)


def material_late_days_enabled(item: LongreadMaterialItem) -> bool:
    estimation = cast(
        LongreadMaterialEstimation | None,
        getattr(item, "estimation", None),
    )
    activity: LongreadMaterialActivity | None = (
        estimation.activity if estimation is not None else None
    )
    return bool(activity.is_late_days_enabled) if activity else False


def matches_homework(
    item: HomeworkItem,
    params: ListHomeworkParams,
) -> bool:
    if (
        params.deadline_passed is not None
        and item.deadline_passed != params.deadline_passed
    ):
        return False
    if (
        params.late_days_available is not None
        and item.late_days_available != params.late_days_available
    ):
        return False
    if params.state and item.state not in params.state:
        return False
    if params.query:
        haystack = " ".join(
            [
                item.title,
                item.course_name,
                item.theme_name,
                item.longread_name,
            ]
        ).casefold()
        if params.query.casefold() not in haystack:
            return False
    return True


def matches_test(item: TestItem, params: ListTestsParams) -> bool:
    if (
        params.deadline_passed is not None
        and item.deadline_passed != params.deadline_passed
    ):
        return False
    if params.state and item.state not in params.state:
        return False
    if params.query:
        haystack = " ".join(
            [
                item.title,
                item.course_name,
                item.theme_name,
                item.longread_name,
            ]
        ).casefold()
        if params.query.casefold() not in haystack:
            return False
    return True
```

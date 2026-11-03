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
  server.py            MCP server, tools, HTTP helper, error mapping
  config.py            pydantic-settings config and auth headers
  models_params.py     query-argument models and query scalar aliases
  models_responses.py  response models, CuBaseModel, material union
  models_errors.py     problem-detail models and status mapping
  models_scalars.py    shared scalar aliases
tests/test_tools.py    live smoke walk
api_docs.yaml          OpenAPI specification snapshot
```

All HTTP goes through `_get_json` in `server.py`:

```python
async def _get_json(
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
  `models_params.py`. Do not embed path IDs in that model.
- Optional params use `params: SomeParams | None = None`; required params stay
  required. `generate_content_download_link` is required because `filename` is
  required.
- `_get_json` accepts only `path` and `params`; never add exclude lists or
  path-ID filtering.
- Tool functions are `async`, return a Pydantic response model, and call
  `Model.model_validate(await _get_json(...))`.
- The server uses stdio transport through `mcp.run(transport="stdio")`.

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
   `_get_json`.
6. Add coverage to `tests/test_tools.py` following the existing smoke-walk
   structure.

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

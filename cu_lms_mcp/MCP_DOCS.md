# CU LMS MCP Guide

Read-only access to the Central University LMS. The server never submits,
edits, or deletes anything in LMS.

## LMS vocabulary

The API names differ from the student-facing UI:

- **Course** — a course the student is enrolled in.
- **Theme** (`theme`) — a **week** in the LMS UI: "Неделя 1", "Неделя 2".
- **Longread** (`longread`) — an unnamed container inside a week. The UI does
  not use the word "longread" and may not display its name.
- **Material** (`LongreadMaterialItem`) — a block inside a longread.

A week usually contains one or more longreads. A longread may hold learning
materials, homework, a test, or another block.

## Material types

- `markdown`, `file`, `image`, `video`, `audio`, `videoPlatform` — learning
  materials; usually text, files, or media.
- `coding` — homework/ДЗ; usually a description plus files.
- `questions` — a test/quiz/КР; questions and options, usually no files.

Only `coding` and `questions` materials expose `task_id`. Use
`get_task(item.task_id)`, not `get_task(item.id)`: `item.id` is the material
ID.

## Typical workflow

1. `get_student_profile` — identify the student and read the late-day balance.
2. `list_student_courses` — choose a course.
3. `get_course_overview` — list weeks and their longreads.
4. `get_course_theme_summary` — inspect one week.
5. `get_longread_materials` — list material blocks in a longread.
6. `get_task` — open homework or a test by `task_id`.
7. `generate_content_download_link` — create a download URL from a material
   `filename` and optional `version`.

## Late days (LD / ЛД)

- Students receive about 50 late days at the start of the semester.
  `lateDaysBalance` is the remaining balance.
- One late day extends an eligible homework deadline by one day. Example:
  Monday 22:00 + 1 late day = Tuesday 22:00.
- Only homework (`coding`) can be extended. Not every homework is eligible:
  check `isLateDaysEnabled` on the material activity or task.
- Tests, quizzes, and КР (`questions`) cannot be extended.
- A task cannot be extended if a solution is already attached. Check
  `TaskSolution` for `attachments`, `answers`, or `solutionUrl`.
- `lateDays` on a task is how many late days are already spent, not the
  remaining balance.

## Tool map

- `get_lms_guide` — this guide.
- `get_student_profile` — profile and late-day balance.
- `list_student_courses` — paginated course list.
- `get_course_summary` — one course.
- `get_course_overview` — weeks and longreads in a course.
- `get_course_theme_summary` — one week/theme.
- `get_longread_summary` — one longread.
- `get_longread_materials` — material blocks in a longread.
- `get_task` — homework or test details.
- `generate_content_download_link` — download URL for a file.

## Notes

- Course and material lists are paginated; default limit is 25.
- Deadlines are timestamps. Compare them in the student's LMS timezone.
- Download links may be pre-signed and should be treated as sensitive.

from __future__ import annotations

from datetime import datetime
from typing import Annotated, ClassVar, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .models_scalars import (
    ActivityId,
    ActivityWeight,
    AttemptId,
    CourseCategory,
    CourseCategoryCover,
    CourseId,
    CourseThemeId,
    ExerciseId,
    FileMediaType,
    ListingOrder,
    LongreadExerciseQuestionsMode,
    LongreadId,
    LongreadMaterialId,
    LongreadMaterialMediaTypeUpper,
    LongreadMaterialType,
    LongreadMaterialVersion,
    LongreadMaterialViewType,
    LongreadType,
    MaxScore,
    PublicationState,
    PublishDate,
    PublishedAt,
    QuestionId,
    QuestionItemScore,
    QuestionOptionId,
    QuestionsSettingsEvalStrategy,
    QuizId,
    StudyLevel,
    SubjectId,
    TaskId,
    TaskScoreSkillLevel,
    TaskState,
    TaskType,
    TimeAccount,
    UniversityEmail,
    UserId,
    VideoPlatformState,
)


class CuBaseModel(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class Paging(CuBaseModel):
    limit: Annotated[int, Field(ge=1)]
    offset: Annotated[int, Field(ge=0)]
    total_count: Annotated[int, Field(ge=0)]


class CourseSettings(CuBaseModel):
    skill_level: str
    is_skill_level_enabled: bool
    syllabus_url: str | None
    time_channel_url: str | None


class CourseBlocker(CuBaseModel):
    enabled: bool
    enable_at: datetime | None
    score: float | None


class CourseSummaryItem(CuBaseModel):
    id: CourseId
    name: str
    state: PublicationState
    publish_date: PublishDate
    published_at: PublishedAt
    settings: CourseSettings
    subject_id: SubjectId
    is_archived: bool
    category: CourseCategory
    commit_level: str | None = None
    category_cover: CourseCategoryCover | None = None
    participation_type: str | None = None
    blocker: CourseBlocker | None = None


class CourseSummaryByIdResponse(CourseSummaryItem):
    pass


class ListStudentCoursesResponse(CuBaseModel):
    items: list[CourseSummaryItem]
    paging: Paging


class CurrentStudentResponse(CuBaseModel):
    id: UserId
    last_name: str
    first_name: str
    middle_name: str | None
    university_email: UniversityEmail
    time_account: TimeAccount
    study_start_year: Annotated[int, Field(ge=1970)] | None
    study_level: StudyLevel
    late_days_balance: Annotated[int, Field(ge=0)]


# ---------------------------------------------------------------------------
# Course overview models
# ---------------------------------------------------------------------------


class ActivityDefinition(CuBaseModel):
    id: ActivityId
    name: str
    weight: ActivityWeight


class ExerciseItem(CuBaseModel):
    id: ExerciseId
    name: str
    max_score: MaxScore
    activity: ActivityDefinition
    deadline: datetime


class LongreadItem(CuBaseModel):
    id: LongreadId
    type: LongreadType
    name: str
    state: PublicationState
    publish_date: PublishDate
    published_at: PublishedAt
    exercises: list[ExerciseItem]


class CourseThemeItem(CuBaseModel):
    id: CourseThemeId
    name: str
    order: ListingOrder
    state: PublicationState
    publish_date: PublishDate
    published_at: PublishedAt
    longreads: list[LongreadItem]


class CourseOverviewByIdResponse(CuBaseModel):
    id: CourseId
    name: str
    is_archived: bool
    state: PublicationState
    publish_date: PublishDate
    published_at: PublishedAt
    settings: CourseSettings
    blocker: CourseBlocker | None
    themes: list[CourseThemeItem]


class CourseThemeSummaryByIdResponse(CuBaseModel):
    id: CourseThemeId
    name: str
    state: PublicationState
    publish_date: PublishDate
    published_at: PublishedAt
    order: ListingOrder
    category: CourseCategory
    category_cover: Annotated[int, Field(ge=0)]


class LongreadSummaryByIdResponse(CuBaseModel):
    id: LongreadId
    type: LongreadType
    name: str
    order: ListingOrder
    state: PublicationState
    publish_date: PublishDate
    published_at: PublishedAt


# ---------------------------------------------------------------------------
# Longread material models
# ---------------------------------------------------------------------------


class LongreadMaterialContent(CuBaseModel):
    name: str
    filename: str
    media_type: LongreadMaterialMediaTypeUpper
    version: LongreadMaterialVersion
    length: Annotated[int, Field(ge=0)]


class LongreadMaterialAttachmentItem(CuBaseModel):
    name: str
    filename: str
    media_type: FileMediaType
    length: Annotated[int, Field(ge=0)]
    version: LongreadMaterialVersion


class LongreadMaterialCoding(CuBaseModel):
    exercise_url: str | None


class LongreadMaterialActivity(CuBaseModel):
    id: ActivityId
    name: str
    weight: ActivityWeight
    max_exercises_count: Annotated[float, Field(ge=1)]
    average_score_threshold: Annotated[float, Field(ge=0)] | None
    is_late_days_enabled: bool
    best_scores_count: int | None


class LongreadMaterialEstimation(CuBaseModel):
    start_date: datetime
    timer: str | None
    max_score: MaxScore | None
    deadline: datetime | None
    activity: LongreadMaterialActivity | None


class ExerciseQuestionsSettings(CuBaseModel):
    questions_per_attempt: None
    attempts_limit: Annotated[int, Field(ge=0)]
    evaluation_strategy: QuestionsSettingsEvalStrategy


class QuestionItemCorrectAnswerInputStringCorrectAnswer(CuBaseModel):
    type: Literal["inputStringCorrectAnswer"]
    variants: list[str]


class QuestionItemCorrectAnswerInputNumberCorrectAnswer(CuBaseModel):
    type: Literal["inputNumberCorrectAnswer"]
    variants: list[float]
    show_precision_hint: bool
    auto_evaluation_precision: (
        Annotated[str, Field(pattern=r"^0(\.0+)?")] | None
    )
    precision: Annotated[int, Field(ge=0)] | None


QuestionItemCorrectAnswer = Annotated[
    QuestionItemCorrectAnswerInputStringCorrectAnswer
    | QuestionItemCorrectAnswerInputNumberCorrectAnswer,
    Field(discriminator="type"),
]


class QuestionItemEvaluationBlock(CuBaseModel):
    correct_answer: QuestionItemCorrectAnswer | None
    auto_evaluation: bool
    recommendation: str | None


class QuestionItemOption(CuBaseModel):
    id: QuestionOptionId
    value: str
    order: ListingOrder
    is_correct: bool
    recommendation: str | None


class SingleChoiceOptions(CuBaseModel):
    options: list[QuestionItemOption]


class MultipleChoiceOptions(CuBaseModel):
    options: list[QuestionItemOption]


class LongreadExerciseInputQuestionItem(CuBaseModel):
    type: Literal["input"]
    id: QuestionId
    order: ListingOrder
    content: str
    score: QuestionItemScore
    attachments: list[LongreadMaterialAttachmentItem]
    correct_answer: QuestionItemCorrectAnswer | None
    auto_evaluation: bool
    recommendation: str | None
    input: QuestionItemEvaluationBlock


class LongreadExerciseSingleChoiceQuestionItem(CuBaseModel):
    type: Literal["singleChoice"]
    id: QuestionId
    order: ListingOrder
    content: str
    score: QuestionItemScore
    attachments: list[LongreadMaterialAttachmentItem]
    options: list[QuestionItemOption]
    are_options_shuffled: bool
    single_choice: SingleChoiceOptions


class LongreadExerciseMultipleChoiceQuestionItem(CuBaseModel):
    type: Literal["multipleChoice"]
    id: QuestionId
    order: ListingOrder
    content: str
    score: QuestionItemScore
    attachments: list[LongreadMaterialAttachmentItem]
    options: list[QuestionItemOption]
    are_options_shuffled: bool
    multiple_choice: MultipleChoiceOptions


LongreadExerciseQuestionItem = Annotated[
    LongreadExerciseInputQuestionItem
    | LongreadExerciseSingleChoiceQuestionItem
    | LongreadExerciseMultipleChoiceQuestionItem,
    Field(discriminator="type"),
]


class LongreadMarkdownMaterialItem(CuBaseModel):
    discriminator: Literal["markdown"]
    state: PublicationState
    view_type: LongreadMaterialViewType
    type: LongreadMaterialType
    id: LongreadMaterialId
    order: ListingOrder
    view_content: str
    publish_date: PublishDate
    published_at: PublishedAt


class LongreadFileMaterialItem(CuBaseModel):
    discriminator: Literal["file"]
    state: PublicationState
    view_type: LongreadMaterialViewType
    type: LongreadMaterialType
    id: LongreadMaterialId
    order: ListingOrder
    media_type: FileMediaType
    filename: str
    version: LongreadMaterialVersion
    length: Annotated[int, Field(ge=0)]
    publish_date: PublishDate
    published_at: PublishedAt
    content: LongreadMaterialContent


class LongreadExerciseCodingMaterialItem(CuBaseModel):
    discriminator: Literal["coding"]
    state: PublicationState
    view_type: LongreadMaterialViewType
    type: LongreadMaterialType
    id: LongreadMaterialId
    order: ListingOrder
    name: str
    view_content: str | None
    estimation: LongreadMaterialEstimation
    reviewers: list[UserId]
    assignees: list[UserId]
    attachments: list[LongreadMaterialAttachmentItem]
    backlogged_at: datetime | None
    task_id: TaskId | None
    is_tracking_students: bool
    is_code_editor_enabled: bool
    exercise_url: str | None
    coding: LongreadMaterialCoding


class LongreadImageMaterialItem(CuBaseModel):
    discriminator: Literal["image"]
    state: PublicationState
    view_type: LongreadMaterialViewType
    type: LongreadMaterialType
    id: LongreadMaterialId
    order: ListingOrder
    image_scale: int | None
    media_type: FileMediaType
    filename: str
    version: LongreadMaterialVersion
    length: Annotated[int, Field(ge=0)]
    publish_date: PublishDate
    published_at: PublishedAt
    content: LongreadMaterialContent


class LongreadExerciseQuestionsMaterialItem(CuBaseModel):
    discriminator: Literal["questions"]
    state: PublicationState
    view_type: LongreadMaterialViewType
    type: LongreadMaterialType
    id: LongreadMaterialId
    order: ListingOrder
    name: str
    view_content: str | None
    estimation: LongreadMaterialEstimation
    reviewers: list[UserId]
    assignees: list[UserId]
    attachments: list[LongreadMaterialAttachmentItem]
    backlogged_at: datetime | None
    task_id: TaskId | None
    is_tracking_students: bool
    mode: LongreadExerciseQuestionsMode | None
    are_questions_shuffled: bool
    settings: ExerciseQuestionsSettings
    quiz_id: QuizId
    questions: list[LongreadExerciseQuestionItem] | None


class LongreadVideoPlatformMaterialItem(CuBaseModel):
    discriminator: Literal["videoPlatform"]
    state: PublicationState
    view_type: LongreadMaterialViewType
    type: LongreadMaterialType
    id: LongreadMaterialId
    order: ListingOrder
    name: str
    description: str
    video_id: UUID
    timecodes: list[object] = Field(max_length=0)
    publish_date: PublishDate
    video_state: VideoPlatformState
    url: str


class LongreadVideoMaterialItem(CuBaseModel):
    discriminator: Literal["video"]
    state: PublicationState
    view_type: LongreadMaterialViewType
    type: LongreadMaterialType
    id: LongreadMaterialId
    order: ListingOrder
    media_type: FileMediaType
    filename: str
    version: LongreadMaterialVersion
    length: Annotated[int, Field(ge=0)]
    publish_date: PublishDate
    published_at: PublishedAt
    content: LongreadMaterialContent


class LongreadAudioMaterialItem(CuBaseModel):
    discriminator: Literal["audio"]
    state: PublicationState
    view_type: LongreadMaterialViewType
    type: LongreadMaterialType
    id: LongreadMaterialId
    order: ListingOrder
    media_type: FileMediaType
    filename: str
    version: LongreadMaterialVersion
    length: Annotated[int, Field(ge=0)]
    publish_date: PublishDate
    published_at: PublishedAt
    content: LongreadMaterialContent


LongreadMaterialItem = Annotated[
    LongreadMarkdownMaterialItem
    | LongreadFileMaterialItem
    | LongreadExerciseCodingMaterialItem
    | LongreadImageMaterialItem
    | LongreadExerciseQuestionsMaterialItem
    | LongreadVideoPlatformMaterialItem
    | LongreadVideoMaterialItem
    | LongreadAudioMaterialItem,
    Field(discriminator="discriminator"),
]


class LongreadMaterialsByIdResponse(CuBaseModel):
    items: list[LongreadMaterialItem]
    paging: Paging


# ---------------------------------------------------------------------------
# Task models
# ---------------------------------------------------------------------------


class TaskAttachment(CuBaseModel):
    name: str
    filename: str
    media_type: FileMediaType
    length: Annotated[int, Field(ge=0)]
    version: LongreadMaterialVersion


class TaskExerciseActivity(CuBaseModel):
    id: ActivityId
    name: str
    weight: ActivityWeight
    is_late_days_enabled: bool


class TaskExerciseQuestionOrderOptionOrder(CuBaseModel):
    option_id: QuestionOptionId
    order: ListingOrder


class TaskExerciseQuestionOrder(CuBaseModel):
    question_id: QuestionId
    order: ListingOrder
    option_orders: list[TaskExerciseQuestionOrderOptionOrder]


class TaskExercise(CuBaseModel):
    id: ExerciseId
    name: str
    type: TaskType
    max_score: MaxScore
    start_date: datetime
    deadline: datetime
    timer: str | None
    activity: TaskExerciseActivity
    question_orders: list[TaskExerciseQuestionOrder] | None
    are_questions_shuffled: bool | None
    quiz_id: QuizId | None
    mode: LongreadExerciseQuestionsMode | None
    is_code_editor_enabled: bool
    view_content: str | None
    exercise_url: str | None
    attachments: list[TaskAttachment] | None
    settings: ExerciseQuestionsSettings | None


class TaskCourse(CuBaseModel):
    id: CourseId
    name: str
    is_archived: bool


class TaskCourseTheme(CuBaseModel):
    id: CourseThemeId
    name: str


class TaskLongread(CuBaseModel):
    id: LongreadId
    name: str


class TaskReviewer(CuBaseModel):
    id: UserId
    name: str
    identity_email: UniversityEmail
    email: UniversityEmail
    identity_identifier: UserId
    time_account: TimeAccount
    last_name: str
    first_name: str
    middle_name: str | None


class TaskSolutionAnswersQuestionInputAnswer(CuBaseModel):
    values: Annotated[list[str], Field(min_length=1)]
    value: None
    recommendation: str


class TaskSolutionAnswersQuestionInputNumberAnswer(CuBaseModel):
    values: Annotated[list[float], Field(min_length=1)]
    value: None
    recommendation: str


class TaskSolutionAnswersQuestionOptionsItem(CuBaseModel):
    id: QuestionOptionId
    is_correct: bool
    recommendation: str | None


class TaskSolutionAnswersQuestionOptionsQuestionItem(CuBaseModel):
    id: QuestionId
    type: Literal["singleChoice", "multipleChoice"]
    answer: None
    options: list[TaskSolutionAnswersQuestionOptionsItem]


class TaskSolutionAnswersQuestionInputQuestionItem(CuBaseModel):
    id: QuestionId
    type: Literal["input"]
    answer: TaskSolutionAnswersQuestionInputAnswer | None
    options: None


class TaskSolutionAnswersQuestionInputNumberQuestionItem(CuBaseModel):
    id: QuestionId
    type: Literal["inputNumber"]
    answer: TaskSolutionAnswersQuestionInputNumberAnswer | None
    options: None


TaskSolutionAnswersQuestion = Annotated[
    TaskSolutionAnswersQuestionOptionsQuestionItem
    | TaskSolutionAnswersQuestionInputQuestionItem
    | TaskSolutionAnswersQuestionInputNumberQuestionItem,
    Field(discriminator="type"),
]


class TaskSolutionAnswersItem(CuBaseModel):
    answer: str | float | list[int]
    question: TaskSolutionAnswersQuestion


class TaskSolution(CuBaseModel):
    type: TaskType
    solution_url: str | None
    answers: list[TaskSolutionAnswersItem] | None
    attachments: list[TaskAttachment] | None


class TaskScoresItem(CuBaseModel):
    question_id: QuestionId
    score: float | None


class TaskByIdResponse(CuBaseModel):
    id: TaskId
    type: TaskType
    state: TaskState
    score: float | None
    score_skill_level: TaskScoreSkillLevel | None
    is_skill_level_enabled: bool
    is_late_days_enabled: bool
    extra_score: float | None
    created_at: datetime
    started_at: datetime | None
    submit_at: datetime | None
    reject_at: datetime | None
    evaluate_at: datetime | None
    deadline: datetime
    late_days: Annotated[int, Field(ge=0)] | None
    exercise: TaskExercise
    course: TaskCourse
    theme: TaskCourseTheme
    longread: TaskLongread
    student: CurrentStudentResponse
    reviewer: TaskReviewer | None
    solution: TaskSolution | None
    scores: list[TaskScoresItem] | None
    quiz_session_id: TaskId | None
    evaluated_attempt_id: AttemptId | None
    current_attempt_id: AttemptId | None
    last_attempt_id: AttemptId | None


class GenerateContentDownloadLinkResponse(CuBaseModel):
    url: str

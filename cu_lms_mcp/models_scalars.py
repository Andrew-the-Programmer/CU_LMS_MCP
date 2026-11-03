from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field

TraceId = Annotated[
    str,
    Field(pattern=r"^00-[0-9a-f]{32}-[0-9a-f]{16}-[0-9a-f]{2}$"),
]

UserId = UUID
UniversityEmail = str
TimeAccount = Annotated[
    str,
    Field(min_length=3, max_length=22, pattern=r"^[a-z][a-z0-9._-]{2,21}$"),
]

CourseId = Annotated[int, Field(ge=0)]
CourseThemeId = Annotated[int, Field(ge=0)]
LongreadId = Annotated[int, Field(ge=0)]
ExerciseId = Annotated[int, Field(ge=0)]
ActivityId = Annotated[int, Field(ge=0)]
TaskId = Annotated[int, Field(ge=0)]
QuestionId = Annotated[int, Field(ge=0)]
QuestionOptionId = Annotated[int, Field(ge=0)]
QuizId = Annotated[int, Field(ge=0)]
AttemptId = Annotated[int, Field(ge=0)]
LongreadMaterialId = Annotated[int, Field(ge=0)]

ListingOrder = Annotated[int, Field(ge=0)]
ActivityWeight = Annotated[float, Field(ge=0, le=1)]
MaxScore = Annotated[float, Field(ge=0)]
QuestionItemScore = Annotated[float, Field(ge=0)]

PublishDate = datetime | None
PublishedAt = datetime | None
SubjectId = int | None

PublicationState = Literal["published", "archived", "draft"]
StudyLevel = Literal["none", "bachelor", "master", "dpo", "dpoMaster"]

CourseSkillLevel = Literal["none"]
CourseCategory = Literal[
    "withoutCategory",
    "general",
    "mathematics",
    "business",
    "development",
    "stem",
    "softSkills",
    "ml",
    "design",
    "analytics",
    "career",
    "management",
]
CourseCategoryCover = Literal[
    "sineWave",
    "curvesGrid",
    "ellipsesOverlap",
    "geometricTriangle",
    "verticalLines",
    "gridPlanes",
    "spiralLoops",
    "symmetricCircles",
]

LongreadType = Literal["common", "handout"]

LongreadMaterialType = Literal[
    "markdown",
    "content",
    "coding",
    "image",
    "questions",
    "videoPlatform",
]
LongreadMaterialDiscriminator = Literal[
    "markdown",
    "file",
    "coding",
    "image",
    "questions",
    "videoPlatform",
    "video",
    "audio",
]
LongreadMaterialViewType = Literal[
    "ngxMarkdown",
    "file",
    "exerciseCoding",
    "image",
    "exerciseQuestions",
    "videoPlatform",
    "video",
    "audio",
]
FileMediaType = Literal["file", "image", "video", "audio"]
LongreadMaterialMediaTypeUpper = Literal["File", "Image", "Video", "Audio"]
LongreadMaterialVersion = Annotated[
    str | None,
    Field(pattern=r"^[0-9a-f]{8}$"),
]

LongreadExerciseQuestionsMode = Literal["atMoment", "byDeadline"]
QuestionsSettingsEvalStrategy = Literal["last", "best"]

VideoPlatformState = Literal[
    "unspecified",
    "empty",
    "uploaded",
    "transcoding",
    "viewable",
    "ready",
    "partiallyReady",
    "error",
]

TaskType = Literal["coding", "questions"]
TaskState = Literal[
    "backlog",
    "inProgress",
    "submitted",
    "review",
    "evaluated",
    "failed",
]
TaskScoreSkillLevel = Literal["none", "basic", "intermediate", "advanced"]

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .models_responses import CuBaseModel
from .models_scalars import PublicationState

LimitQuery = Annotated[
    int,
    Field(ge=1, description="Maximum number of items to return."),
]
OffsetQuery = Annotated[
    int,
    Field(
        ge=0,
        description="Number of items to skip before collecting result items.",
    ),
]

VersionType = Annotated[
    str,
    Field(
        pattern=r"^[0-9a-f]{8}$",
        description="Material content revision identifier.",
    ),
]


class ListStudentCoursesParams(CuBaseModel):
    limit: LimitQuery = 25
    offset: OffsetQuery = 0
    state: list[PublicationState] | None = Field(
        default=None,
        description="Include only courses whose state matches any of the values.",
    )


class LongreadMaterialsParams(CuBaseModel):
    limit: LimitQuery = 25
    offset: OffsetQuery = 0


class ContentDownloadLinkParams(CuBaseModel):
    filename: str = Field(description="File object path in storage.")
    version: VersionType | None = None

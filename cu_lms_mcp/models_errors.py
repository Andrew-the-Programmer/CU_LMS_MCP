from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .models_responses import CuBaseModel
from .models_scalars import TraceId

HttpStatus = Annotated[int, Field(ge=100, le=599)]


class BaseProblemError(BaseModel):
    type: str | None = None
    title: str
    status: HttpStatus
    trace_id: TraceId | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


class BaseBadRequestError(CuBaseModel):
    title: str
    status: HttpStatus
    errors: dict[str, list[str]]


class BaseUnauthorizedError(CuBaseModel):
    type: str | None = None
    title: str
    status: HttpStatus
    trace_id: TraceId


class BaseForbiddenError(CuBaseModel):
    type: str | None = None
    title: str
    status: HttpStatus
    detail: str | None = None
    instance: str | None = None
    trace_id: TraceId


class BaseNotFoundError(CuBaseModel):
    title: str
    status: HttpStatus
    detail: str | None = None
    instance: str | None = None
    entity_id: int | None = None
    trace_id: TraceId


DefaultError = BaseProblemError
BadRequestError = BaseBadRequestError
UnauthorizedError = BaseUnauthorizedError
ForbiddenError = BaseForbiddenError
NotFoundError = BaseNotFoundError


ERROR_RESPONSES: dict[int, type[CuBaseModel]] = {
    400: BadRequestError,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
}

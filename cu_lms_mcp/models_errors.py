from __future__ import annotations

from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .models_scalars import TraceId

HttpStatus = Annotated[int, Field(ge=100, le=599)]


class BaseError(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


class BaseProblemError(BaseError):
    type: str | None = None
    title: str
    status: HttpStatus
    trace_id: TraceId | None = None

    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


class BaseBadRequestError(BaseError):
    title: str
    status: HttpStatus
    errors: dict[str, list[str]]


class BaseUnauthorizedError(BaseError):
    type: str | None = None
    title: str
    status: HttpStatus
    trace_id: TraceId


class BaseForbiddenError(BaseError):
    type: str | None = None
    title: str
    status: HttpStatus
    detail: str | None = None
    instance: str | None = None
    trace_id: TraceId


class BaseNotFoundError(BaseError):
    title: str | None = None
    status: HttpStatus
    detail: str | None = None
    instance: str | None = None
    entity_id: int | None = None
    trace_id: TraceId


ERROR_RESPONSES: dict[int, type[BaseError]] = {
    400: BaseBadRequestError,
    401: BaseUnauthorizedError,
    403: BaseForbiddenError,
    404: BaseNotFoundError,
}

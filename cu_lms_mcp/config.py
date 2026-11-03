from functools import lru_cache
from multiprocessing import Value
from typing import Callable, ClassVar, NoReturn

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def require(name: str) -> Callable[[], NoReturn]:
    def r() -> NoReturn:
        raise ValueError(f"Set {name.upper()} in .env")

    return r


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_prefix="CU_LMS_",
        case_sensitive=False,
    )

    session_cookie: SecretStr = Field(
        default_factory=require("CU_LMS_SESSION_COOKIE"),
        description="Value of the bff.cookie session cookie from my.centraluniversity.ru",
    )
    base_url: str = Field(
        default="https://my.centraluniversity.ru/api/micro-lms",
        description="Base URL for the CU LMS API",
    )
    timeout: float = Field(
        default=30.0, gt=0, description="HTTP timeout in seconds"
    )

    @property
    def auth_headers(self) -> dict[str, str]:
        return {
            "accept": "application/json",
            "cookie": f"bff.cookie={self.session_cookie.get_secret_value()}",
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()

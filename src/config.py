from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str

    jwt_secret: str
    jwt_expires_minutes: int = 60

    cookie_domain: str | None = None
    cookie_secure: bool

    cors_allowed_origins: str = ""

    azure_storage_connection_string: str | None = None
    azure_storage_account_url: str | None = None
    azure_storage_public_blob_endpoint: str

    servicebus_connection_string: str | None = None
    queue_name: str = "image-jobs"
    sas_ttl_minutes: int = 15

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.cors_allowed_origins.split(",") if o.strip()]

    @field_validator("cookie_domain", "azure_storage_connection_string", "azure_storage_account_url", mode="before")
    @classmethod
    def _blank_to_none(cls, v: str | None) -> str | None:
        return v or None


@lru_cache
def get_settings() -> Settings:
    return Settings()

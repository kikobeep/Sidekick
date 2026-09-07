"""网页搜索提供商的环境配置。"""

from enum import StrEnum
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_CONFIG_FILE = Path(__file__).resolve().parents[3] / ".config"


class SearchProviderName(StrEnum):
    AUTO = "auto"
    TAVILY = "tavily"


class SearchSettings(BaseSettings):
    """从 backend/.config 和进程环境读取搜索配置。"""

    model_config = SettingsConfigDict(
        env_file=_BACKEND_CONFIG_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    search_provider: SearchProviderName = SearchProviderName.TAVILY
    tavily_api_key: SecretStr | None = None
    search_timeout_seconds: float = Field(default=15.0, gt=0, le=60)
    search_max_results: int = Field(default=5, ge=1, le=10)

    def tavily_api_key_value(self) -> str | None:
        if self.tavily_api_key is None:
            return None
        value = self.tavily_api_key.get_secret_value().strip()
        return value or None


__all__ = ["SearchProviderName", "SearchSettings"]

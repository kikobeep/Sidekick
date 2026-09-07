from abc import ABC,abstractmethod
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import StrEnum

class SearchDepth(StrEnum):
    BASIC = "basic"
    ADVANCED = "advanced"
    FAST = "fast"
    ULTRA = "ultra-fast"

class SearchTopic(StrEnum):
    GENERAL = "general"
    NEWS = "news"
    FINANCE = "finance"

class SearchRange(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    query: str = Field(max_length=500)
    search_depth: SearchDepth = SearchDepth.BASIC
    max_results: int = Field(default=5, ge=1, le=10)
    topic: SearchTopic = SearchTopic.GENERAL
    time_range: SearchRange | None = None
    include_domains: tuple[str, ...] = Field(default=(), max_length=10)
    exclude_domains: tuple[str, ...] = Field(default=(), max_length=10)

    @field_validator("query")
    @classmethod
    def clean_query(cls, value: str) -> str:
        query = " ".join(value.split())
        if not query:
            raise ValueError("query cannot be empty")
        return query

class SearchResult(BaseModel):
    """单条搜索结果。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    title: str
    url: str
    content: str
    score: float | None = None
    favicon: str | None = None

class SearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    query: str
    answer: str
    results: tuple[SearchResult, ...]
    response_time: float | None = Field(default=None, ge=0)
    backup_used: bool = False


class SearchProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...
    
    @abstractmethod
    async def search(self,request: SearchRequest) -> SearchResponse:
        ...

class SearchNetworkError(RuntimeError):
    """搜索服务网络或 HTTP 请求失败。"""


class SearchResponseError(RuntimeError):
    """搜索服务返回无法解析的数据。"""

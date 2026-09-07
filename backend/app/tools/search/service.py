"""搜索服务及 Tavily 配置工厂。"""

from .base import (
    SearchNetworkError, SearchProvider, SearchRequest, SearchResponse,
    SearchResponseError,
)
from .settings import SearchSettings
from .tavily import TavilySearchProvider


class SearchService:
    def __init__(
        self,
        primary_provider: SearchProvider,
        backup_provider: SearchProvider | None = None,
    ) -> None:
        self._primary = primary_provider
        self._backup = backup_provider

    @property
    def primary_provider(self) -> str:
        return self._primary.name

    async def search(self, request: SearchRequest) -> SearchResponse:
        try:
            return await self._primary.search(request)
        except (SearchNetworkError, SearchResponseError):
            if self._backup is None:
                raise
            response = await self._backup.search(request)
            return response.model_copy(update={"backup_used": True})


def build_search_service(config: SearchSettings) -> SearchService:
    # auto 暂时也使用 Tavily；不启用其他搜索引擎。
    api_key = config.tavily_api_key_value()
    if api_key is None:
        raise ValueError("Tavily search requires TAVILY_API_KEY")
    return SearchService(TavilySearchProvider(
        api_key, timeout_seconds=config.search_timeout_seconds,
    ))


build_service_from_config = build_search_service

__all__ = ["SearchService", "build_search_service", "build_service_from_config"]

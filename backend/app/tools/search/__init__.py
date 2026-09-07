"""网页搜索的公共接口。"""

from .base import (
    SearchNetworkError, SearchProvider, SearchRequest, SearchResponse,
    SearchResponseError, SearchResult,
)
from .service import SearchService, build_search_service, build_service_from_config
from .settings import SearchProviderName, SearchSettings
from .tavily import TavilySearchProvider

__all__ = [
    "SearchNetworkError", "SearchProvider", "SearchRequest", "SearchResponse",
    "SearchResponseError", "SearchResult", "SearchService", "SearchSettings",
    "SearchProviderName", "TavilySearchProvider", "build_search_service",
    "build_service_from_config",
]

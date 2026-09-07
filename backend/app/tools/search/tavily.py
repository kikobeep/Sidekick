"""Tavily 异步搜索与响应解析。"""

from typing import Any

import httpx
from pydantic import ValidationError

from .base import (
    SearchNetworkError, SearchProvider, SearchRequest, SearchResponse,
    SearchResponseError, SearchResult,
)


class TavilySearchProvider(SearchProvider):
    def __init__(self, api_key: str, *, timeout_seconds: float = 15.0):
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("Tavily API key cannot be empty")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key.strip()
        self._timeout_seconds = timeout_seconds
        self.url = "https://api.tavily.com/search"

    @property
    def name(self) -> str:
        return "tavily"

    async def search(self, request: SearchRequest) -> SearchResponse:
        payload: dict[str, Any] = {
            "query": request.query,
            "search_depth": request.search_depth.value,
            "topic": request.topic.value,
            "max_results": request.max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        if request.time_range is not None:
            payload["time_range"] = request.time_range.value
        if request.include_domains:
            payload["include_domains"] = list(request.include_domains)
        if request.exclude_domains:
            payload["exclude_domains"] = list(request.exclude_domains)

        response = await self._post(payload)
        try:
            body = response.json()
        except ValueError as exc:
            raise SearchResponseError("Tavily returned invalid JSON") from exc
        if not isinstance(body, dict) or not isinstance(body.get("results"), list):
            raise SearchResponseError("Tavily response missing results list")

        results: list[SearchResult] = []
        try:
            for item in body["results"][:request.max_results]:
                if not isinstance(item, dict):
                    raise SearchResponseError("Tavily result must be an object")
                results.append(SearchResult(
                    title=item.get("title") or "",
                    url=item["url"],
                    content=item.get("content") or "",
                    score=item.get("score"),
                    favicon=item.get("favicon") or None,
                ))
            return SearchResponse(
                query=request.query,
                answer=body.get("answer") or "",
                results=tuple(results),
                response_time=body.get("response_time"),
            )
        except (ValidationError, KeyError) as exc:
            raise SearchResponseError("Tavily returned invalid result data") from exc

    async def _post(self, payload: dict[str, Any]) -> httpx.Response:
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(self.url, json=payload, headers=headers)
            response.raise_for_status()
            return response
        except httpx.TimeoutException as exc:
            phase = {
                httpx.ConnectTimeout: "连接超时（DNS/TCP/TLS）",
                httpx.ReadTimeout: "等待响应超时",
                httpx.WriteTimeout: "发送请求超时",
                httpx.PoolTimeout: "等待可用连接超时",
            }.get(type(exc), "请求超时")
            raise SearchNetworkError(
                f"Tavily request failed [{type(exc).__name__}]: {phase}; "
                f"当前超时阈值为 {self._timeout_seconds:g} 秒。"
                "可在 backend/.config 中调整 SEARCH_TIMEOUT_SECONDS（最大 60 秒）。"
            ) from exc
        except httpx.HTTPError as exc:
            detail = str(exc).strip() or "HTTP 请求失败，异常未提供详细信息"
            raise SearchNetworkError(
                f"Tavily request failed [{type(exc).__name__}]: {detail}"
            ) from exc

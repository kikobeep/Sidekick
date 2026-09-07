"""基础的内置工具。"""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.sandbox import SandboxSupervisor

from ..register import ToolRegistry
from ..search import SearchSettings


def basic_tool_registry(
    workspace_root: str | Path | None = None,
    *,
    search_settings: SearchSettings | None = None,
    sandbox_supervisor: SandboxSupervisor | None = None,
) -> ToolRegistry:
    """创建注册了全部内置工具的工具注册表。"""

    from .current_time import CurrentTimeTool
    from .http_request import HttpRequestTool
    from .list_files import ListFilesTool
    from .read_file import ReadFileTool
    from .shell import ShellCommandTool
    from .web_search import WebSearchTool
    from .write_file import WriteFileTool

    registry = ToolRegistry()
    registry.register(CurrentTimeTool())
    registry.register(ListFilesTool(workspace_root))
    registry.register(ReadFileTool(workspace_root))
    registry.register(WriteFileTool(workspace_root))
    registry.register(
        ShellCommandTool(
            workspace_root,
            sandbox_supervisor=sandbox_supervisor,
        )
    )
    registry.register(HttpRequestTool())
    registry.register(WebSearchTool(settings=search_settings))
    return registry

__all__ = [
    "CurrentTimeTool",
    "HttpRequestTool",
    "ListFilesTool",
    "ReadFileTool",
    "ShellCommandTool",
    "WebSearchTool",
    "WriteFileTool",
    "basic_tool_registry",
]


_TOOL_MODULES = {
    "CurrentTimeTool": "current_time",
    "HttpRequestTool": "http_request",
    "ListFilesTool": "list_files",
    "ReadFileTool": "read_file",
    "ShellCommandTool": "shell",
    "WebSearchTool": "web_search",
    "WriteFileTool": "write_file",
}


def __getattr__(name: str):
    """按需导入工具，让独立搜索不依赖其他工具的运行环境。"""
    if name not in _TOOL_MODULES:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(f".{_TOOL_MODULES[name]}", __name__), name)
    globals()[name] = value
    return value

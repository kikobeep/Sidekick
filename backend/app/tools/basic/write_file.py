"""仅允许写入 Vesta 工作区的 UTF-8 文本工具。"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from app.models.types import ToolDefinition

from ..base import BaseTool
from ._workspace import resolve_workspace_path, workspace_root_path


class WriteFileTool(BaseTool):
    def __init__(self, workspace_root: str | Path | None = None) -> None:
        self._workspace_root = workspace_root_path(workspace_root)

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="write_file",
            description="Write UTF-8 text to a file inside the local workspace.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to the workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete text content to write.",
                    },
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
            strict=True,
            closing_allowed=True,
        )

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        relative_path = arguments.get("path")
        content = arguments.get("content")
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError("'path' must be a non-empty string")
        if not isinstance(content, str):
            raise ValueError("'content' must be a string")

        target = resolve_workspace_path(self._workspace_root, relative_path)
        await asyncio.to_thread(_write_utf8_file, target, content)
        return {
            "path": target.relative_to(self._workspace_root).as_posix(),
            "characters": len(content),
        }


def _write_utf8_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

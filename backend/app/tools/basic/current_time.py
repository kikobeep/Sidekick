"""按需查询当前时间的只读工具。"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.models.types import ToolDefinition, ToolPermission

from ..base import BaseTool


class CurrentTimeTool(BaseTool):
    """返回系统本地时间或指定 IANA 时区的当前时间。"""
    @property
    def definition(self) -> ToolDefinition:

    definition = ToolDefinition(
        name="get_current_time",
        record_output=False,
        description=(
            "Get the actual current date and time on demand. Use this before "
            "answering questions involving today, tomorrow, yesterday, now, "
            "recent dates, deadlines, or relative time. If no timezone is given, "
            "the Vesta process local timezone is used. This is read-only and "
            "does not require approval."
        ),
        parameters={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": (
                        "Optional IANA timezone, such as Asia/Shanghai or "
                        "America/New_York."
                    ),
                }
            },
            "additionalProperties": False,
        },
        permission=ToolPermission.ALLOWED,
    )

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        timezone = arguments.get("timezone")
        if timezone is not None and not isinstance(timezone, str):
            raise TypeError("timezone 必须是字符串")

        if timezone is None or not timezone.strip():
            current = datetime.now().astimezone()
            timezone_name = _local_timezone_name(current)
        else:
            normalized = timezone.strip()
            try:
                zone = ZoneInfo(normalized)
            except ZoneInfoNotFoundError as exc:
                raise ValueError(f"未知 IANA 时区: {normalized}") from exc
            current = datetime.now(zone)
            timezone_name = normalized

        return {
            "datetime": current.isoformat(timespec="seconds"),
            "date": current.date().isoformat(),
            "time": current.time().isoformat(timespec="seconds"),
            "timezone": timezone_name,
            "utc_offset": current.strftime("%z")[:3] + ":" + current.strftime("%z")[3:],
            "unix_timestamp": int(current.timestamp()),
        }


def _local_timezone_name(current: datetime) -> str:
    key = getattr(current.tzinfo, "key", None)
    if isinstance(key, str) and key:
        return key
    return current.tzname() or str(current.tzinfo)


__all__ = ["CurrentTimeTool"]

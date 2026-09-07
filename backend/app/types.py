"""各模块共用的数据类型。"""

from enum import StrEnum


class AgentMode(StrEnum):
    DEFAULT = "default"
    PLAN = "plan"

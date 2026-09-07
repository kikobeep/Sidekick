"""工具注册、查找与定义筛选。"""

from collections.abc import Collection

from app.types import AgentMode

from .availability import ToolAvailabilityPolicy
from .base import BaseTool, ToolDefinition


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self._on_demand_names: set[str] = set()
        self._mode_policy = ToolAvailabilityPolicy()

    def register(self, tool: BaseTool, *, on_demand: bool = False) -> None:
        name = tool.definition.name
        if not name.strip():
            raise ValueError("Tool name cannot be empty")
        if name in self._tools:
            raise ValueError(f"Tool {name!r} is already registered")

        self._tools[name] = tool
        if on_demand:
            self._on_demand_names.add(name)

    def get(self, name: str) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError:
            raise KeyError(f"Tool {name!r} is not registered") from None

    def unregister(self, name: str) -> None:
        try:
            self._tools.pop(name)
        except KeyError:
            raise KeyError(f"Tool {name!r} is not registered") from None
        self._on_demand_names.discard(name)

    def is_on_demand(self, name: str) -> bool:
        return name in self._on_demand_names

    def get_on_demand(self) -> tuple[str, ...]:
        return tuple(sorted(self._on_demand_names))

    def allowed_names_for_mode(self, mode: AgentMode) -> frozenset[str]:
        """返回当前模式允许的已注册工具名称。"""
        return self._mode_policy.allowed_tool_names(
            mode,
            registered_names=self._tools,
        )

    def is_allowed_for_mode(self, name: str, mode: AgentMode) -> bool:
        """仅检查模式限制，不检查按需激活状态。"""
        return name in self.allowed_names_for_mode(mode)

    def definitions_for_mode(
        self,
        mode: AgentMode,
        *,
        activated_names: Collection[str] = (),
    ) -> list[ToolDefinition]:
        """返回满足模式限制和激活条件的工具定义。"""
        allowed = self.allowed_names_for_mode(mode)
        activated = set(activated_names)
        definitions = []

        for name, tool in self._tools.items():
            if name not in allowed:
                continue
            if not self._mode_policy.is_activation_satisfied(
                name,
                mode,
                on_demand_names=self._on_demand_names,
                activated_names=activated,
            ):
                continue
            definitions.append(tool.definition)

        return definitions

    def is_closing_allowed(self, name: str, mode: AgentMode) -> bool:
        """检查模式限制和收尾标记；激活条件由定义筛选处理。"""
        if not self.is_allowed_for_mode(name, mode):
            return False
        return self._tools[name].definition.closing_allowed

    def closing_definitions_for_mode(
        self,
        mode: AgentMode,
        *,
        activated_names: Collection[str] = (),
    ) -> list[ToolDefinition]:
        """返回当前可见且允许在收尾阶段使用的工具定义。"""
        return [
            definition
            for definition in self.definitions_for_mode(
                mode,
                activated_names=activated_names,
            )
            if definition.closing_allowed
        ]

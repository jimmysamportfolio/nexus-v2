from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class SubagentInfo:
    name: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    when_to_use: str = ""

    def format_for_prompt(self) -> str:
        lines = [
            f"**{self.name}**: {self.description}",
            f"  - Tools: {', '.join(self.capabilities)}",
            f"  - Use when: {self.when_to_use}",
        ]
        return "\n".join(lines)

class SubagentRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, SubagentInfo] = {}

    def register(self, subagent: SubagentInfo) -> None:
        self._registry[subagent.name] = subagent

    def get(self, name: str) -> SubagentInfo | None:
        return self._registry.get(name)

    def get_all(self) -> dict[str, SubagentInfo]:
        return self._registry

    def format_for_prompt(self) -> str:
        if not self._registry:
            return "No subagents currently registered."
        
        return "\n\n".join(info.format_for_prompt() for info in self._registry.values())

# Global registry instance
registry = SubagentRegistry()

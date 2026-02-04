from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path

class ToolKind(str, Enum):
    READ = "read"
    WRITE = "write"
    NETWORK = "network"
    MEMORY = "memory"
    MCP = "mcp"

@dataclass
class ToolResult:
    success: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success_result(
        cls,
        output: str,
        metadata: dict | None = None
    ) -> ToolResult:
        return cls(
            success=True,
            output=output,
            error=None,
            metadata=metadata or {}
        )

    @classmethod
    def error_result(cls, error: str, metadata: dict | None = None) -> "ToolResult":
        return cls(
            success=False,
            output="",
            error=error,
            metadata=metadata or {}
        )

@dataclass
class ToolConfirmation:
    tool_name: str
    params: dict[str, Any]
    description: str

@dataclass
class ToolInvocation:
    cwd: Path
    params: dict[str, Any]

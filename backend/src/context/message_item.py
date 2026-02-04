from typing import Any
from dataclasses import dataclass

@dataclass
class MessageItem:
    role: str
    content: str
    token_count: int | None = None
    tool_call_id: str | None = None

    # for passing to OpenAI client
    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "role": self.role,
            "content": self.content,
        }

        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id

        return result
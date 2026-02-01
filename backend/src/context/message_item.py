from typing import Any
from dataclasses import dataclass

@dataclass
class MessageItem:
    role: str
    content: str
    token_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role
            "content": self.content
        }
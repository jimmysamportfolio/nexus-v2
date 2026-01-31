from __future__ import annotations
from typing import Any, List, Dict, Optional

class ContextManager:
    def __init__(self) -> None:
        self._messages: List[Dict[str, Any]] = []

    def add_message(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, Any]]:
        return self._messages

    def get_last_message(self) -> Optional[Dict[str, Any]]:
        if not self._messages:
            return None
        return self._messages[-1]

    def clear(self) -> None:
        self._messages = []

    def add_error(self, error: str) -> None:
        self._messages.append({"role": "system", "content": f"Error: {error}"})

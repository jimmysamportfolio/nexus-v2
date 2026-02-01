from __future__ import annotations
from prompts import get_system_prompt
from message_item import MessageItem
from config import config
from typing import Any, List

class ContextManager:
    def __init__(self) -> None:
        self._system_prompt = get_system_prompt()
        self._model_name = config.DEFAULT_AI_MODEL
        self._messages: List[MessageItem] = []

    def add_user_message(self, content: str) -> None:
        item = MessageItem(
            role="user",
            content=content,
            token_count=count_tokens(content, self._model_name)
        )
        self._messages.append(item)

    def add_assistant_message(self, content: str) -> None:
        item = MessageItem(
            role="assistant",
            content=content,
            token_count=count_tokens(content, self._model_name)
        )
        self._messages.append(item)

    def get_messages(self) -> List[dict[str, Any]]:
        messages = []

        if self._system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": self._system_prompt,
                }
            )
        
        for item in self._messages:
            messages.append(item.to_dict())

        return messages
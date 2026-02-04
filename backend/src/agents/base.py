from __future__ import annotations
from typing import AsyncGenerator

from context import ContextManager
from llm import LLMClient, StreamEventType, ToolCall, ToolResultMessage
from tools import create_default_registry

from .events import AgentEvent, AgentEventType

class BaseAgent:
    def __init__(self):
        self.client = LLMClient()
        self._context_manager = ContextManager()
        self._tool_registry = create_default_registry()

    async def run(self, message: str):
        yield AgentEvent.agent_start(message)

        self._context_manager.add_user_message(message)

        final_response: str | None = None
        
        async for event in self._agentic_loop():
            yield event

            if event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")
        
        yield AgentEvent.agent_end(final_response)

    async def _agentic_loop(self) -> AsyncGenerator[AgentEvent, None]:
        response_text = ""

        tool_schemas = self._tool_registry.get_schemas()
        tool_calls: list[ToolCall] = []
        
        async for event in self.client.chat_completion(
            self._context_manager.get_messages(),
            tools=tool_schemas if tool_schemas else None,
            stream=True
        ):
            if event.type == StreamEventType.TEXT_DELTA:
                if event.text_delta:
                    content = event.text_delta.content
                    response_text += content
                    yield AgentEvent.text_delta(content)
            if event.type ==StreamEventType.TOOL_CALL_COMPLETE:
                if event.tool_call:
                    tool_calls.append(event.tool_call)
            elif event.type == StreamEventType.ERROR:
                yield AgentEvent.agent_error(event.error or "Unknown error occured")
                
        # context management
        self._context_manager.add_assistant_message(
                response_text or None
        )
        if response_text:
            yield AgentEvent.text_complete(response_text)

        # tool calls
        tool_call_results: list[ToolResultMessage] = []
        for tool_call in tool_calls:
            yield AgentEvent.tool_call_start(
                tool_call.call_id,
                tool_call.name,
                tool_call.arguments,
            )
            result = await self._tool_registry.invoke(
                tool_call.name,
                tool_call.arguments,
            )
            yield AgentEvent.tool_call_complete(
                tool_call.call_id,
                tool_call.name,
                result
            )
            tool_call_results.append(
                ToolResultMessage(
                    tool_call_id=tool_call.call_id,
                    content=result.to_model_output(),
                    is_error=not result.success,
                )
            )

        for tool_call in tool_call_results:
            self._context_manager.add_tool_result(
                tool_call.tool_call_id,
                tool_call.content,
            )
        

    async def __aenter__(self) -> BaseAgent:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.client:
            await self.client.close()
            self.client = None

    
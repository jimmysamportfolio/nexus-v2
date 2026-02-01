---
trigger: always_on
---

# Nexus v2 - AI Rules & Guidelines

## Tech Stack
- **Frontend**: Next.js (React), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: MongoDB

## Coding Standards
### General
- **Paths**: Always use absolute paths for file operations.
- **Naming**: Use descriptive variable and function names.
- **Configuration**: Always use `config.py` for variables. Do NOT use `os.getenv` in other files.
- **Cleanliness**: Minimize `print()` statements.
- **Readability**: Use descriptive, human-readable variable names.
- **Modularity**: Pro-actively suggest modularity improvements.
- **Scope**: STRICTLY follow the user request. Do NOT do anything outside of the scope of the question asked.
- **Minimal Changes**: Do not add code or parameters (e.g., `flush=True`) unless absolutely necessary. If an improvement is possible but not requested, suggest it in the chat instead of implementing it directly.
- **Comments**: Add comments for complex logic, new tools, or non-obvious parameters.
- **Docstrings**: Do NOT add long class/function descriptions (docstrings) at the start of functions/classes.

### Frontend (Next.js)
- Use Functional Components with TypeScript interfaces.
- Prefer server components where possible.
- Use `const` for definitions.
- Tailwind CSS for styling with Radix UI wherever possible

### Backend (Python)
- Follow PEP 8 style guide.
- Handle exceptions gracefully.

## Agent Behavior
- **Proactiveness**: Verify files exist before editing.
- **Context**: Read `README.md` or related files if context is missing.
- **Testing**: Run tests after significant changes if available.
- **Implementation Plans**: Do NOT update the `implementation_plan.md` for small, incremental requests made AFTER the initial plan has been implemented. Just execute the request or create a small secondary plan if needed.

### Module Exports
- Always update [__init__.py](cci:7://file:///c:/Users/JimEl/OneDrive/Desktop/Projects/nexus-v2/backend/src/agents/__init__.py:0:0-0:0) when adding new modules/classes to export key symbols for cleaner imports.

## Coding Standards Examples

### Configuration
**BAD:**
```python
api_key = os.getenv("API_KEY") # Don't do this in random files
```

**GOOD:**
```python
# In config.py
class Config:
    API_KEY = os.getenv("API_KEY")

# In other files
from config import config
client = Client(api_key=config.API_KEY)
```

### Docstrings & Comments
**BAD:**
```python
def process_data(data):
    """
    This function processes the data by iterating through it and 
    applying the transformation logic to each item to ensure
    it is in the correct format.
    Args:
        data: The input data
    """
    # Initialize result list
    result = [] 
    for item in data:
        # Check if item is valid
        if item.is_valid():
             result.append(item) # Add to result
```

**GOOD:**
```python
def process_data(data: list[Item]) -> list[Item]:
    return [item for item in data if item.is_valid()]
```

### Scope & Cleanliness
**BAD:**
```python
# User asked to fix a bug in calculation
print(f"Debug: starting calculation with {x}") # Don't add print
logger.info("Starting...") # Don't add logging unless asked
# ... refactoring unrelated code ... # Don't touch unrelated code
```

**GOOD:**
```python
# User asked to fix a bug in calculation
result = x * y # Fix the bug only
```

### Preferred Coding Style Examples

#### Client/Class Structure
```python
from openai import APIConnectionError, RateLimitError, AsyncOpenAI, APIError
import asyncio
from typing import Any, AsyncGenerator
from config import config
from client.response import StreamEvent, TokenUsage

class LLMClient:
    def __init__(self) -> None:
        self._client : AsyncOpenAI | None = None
        self._max_retries: int = config.MAX_RETRIES

    def get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=config.OPENROUTER_API_KEY,
                base_url=config.BASE_URL,
            )
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None

    async def chat_completion(
        self, 
        messages: list[dict[str, Any]],
        stream: bool=True
    ) -> AsyncGenerator[StreamEvent, None]:
        client = self.get_client()

        kwargs = {
            "model": config.DEFAULT_AI_MODEL,
            "messages": messages,
            "stream": stream
        }
    
        for attempt in range(self._max_retries + 1):
            try:
                if stream:
                    async for event in self._stream_response(client, kwargs):
                        yield event
                else:
                    event = await self._non_stream_response(client, kwargs)
                    yield event
                return 

            except RateLimitError as e:
                if attempt < self._max_retries:
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent.create_error(f"Rate Limit Error: {e}")
                    return

            except APIConnectionError as e:
                if attempt < self._max_retries:
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent.create_error(f"Connection error: {e}")
                    return

            except APIError as e:
                yield StreamEvent.create_error(f"API error: {e}")
                return
```

#### Dataclasses
```python
from __future__ import annotations
from client.response import TokenUsage
from typing import Any
from enum import Enum
from dataclasses import dataclass, field

class AgentEventType(str, Enum):
    # Agent lifecyle
    AGENT_START= "agent_start"
    AGENT_END = "agent_end"
    AGENT_ERROR = "agent_error"

    # Text streaming
    TEXT_DELTA = "text_delta"
    TEXT_COMPLETE = "text_complete"

@dataclass
class AgentEvent:
    type: AgentEventType
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def agent_start(
        cls,
        message: str
    ) -> AgentEvent:
        return cls(
            type=AgentEventType.AGENT_START,
            data={
                "message": message,
            },
        )
```
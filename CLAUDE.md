# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nexus v2 is an AI event production agent system with a Next.js frontend and Python backend. The backend implements a modular architecture with subagent routing, tool management, and context management for streaming AI responses via OpenRouter.

## Commands

### Frontend (from `frontend/`)
```bash
npm install          # Install dependencies
npm run dev          # Start development server
npm run build        # Production build
npm run lint         # Run ESLint
```

### Backend (from `backend/`)
```bash
python -m venv venv                    # Create virtual environment
venv\Scripts\activate                  # Activate venv (Windows)
source venv/bin/activate               # Activate venv (Unix)
pip install -r requirements.txt        # Install dependencies
python src/tests/test_agents.py        # Run agent tests (accepts optional prompt arg)
python src/main.py                     # Run backend (server not yet implemented)
```

## Architecture

### Backend Core Systems

**Agents** (`src/agents/`): Event-driven agent system with async streaming
- `BaseAgent`: Main agent class that processes messages and yields `AgentEvent` objects
- `AgentEventType`: START, END, ERROR, TEXT_DELTA, TEXT_COMPLETE
- `subagents/`: Registry system for specialized agent plugins (extensible)

**LLM Client** (`src/llm/`): OpenRouter API integration
- Async streaming with retry logic and exponential backoff
- `StreamEvent` and `TokenUsage` response schemas

**Context Management** (`src/context/`): Message history handling
- `ContextManager`: Manages conversation history and system prompts
- `MessageItem`: Individual messages with token counting via tiktoken

**Tools** (`src/tools/`): Tool abstraction layer
- `BaseTool`: Abstract base class for all tools
- `ToolKind`: READ, WRITE, NETWORK, MEMORY, MCP
- Validation and OpenAI-compatible schema generation

**Prompts** (`src/prompts/`): System prompt generation with subagent definitions

### Data Flow
1. User input → `BaseAgent.run()`
2. Message added to `ContextManager`
3. `LLMClient` streams response via OpenRouter API
4. Events yielded to caller (TEXT_DELTA, TEXT_COMPLETE, ERROR)

### Frontend
- Next.js App Router with React 19 and TypeScript
- Tailwind CSS 4 for styling
- API client in `src/lib/api.ts`

## Key Conventions

- **Configuration**: Always use `config.py` for environment variables. Never use `os.getenv` elsewhere.
- **Module Exports**: Update `__init__.py` when adding new modules/classes.
- **Paths**: Use absolute paths for file operations.
- **Async-first**: Backend uses async patterns throughout.
- **Type Safety**: Pydantic models for validation, TypeScript interfaces for frontend.
- **Minimal Docstrings**: No long descriptions in docstrings; use comments only for complex logic.

## Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript 5, Tailwind CSS 4
- **Backend**: Python 3.11+, OpenAI SDK (OpenRouter), Pydantic 2, httpx, tiktoken
- **Database**: MongoDB (planned, not yet implemented)

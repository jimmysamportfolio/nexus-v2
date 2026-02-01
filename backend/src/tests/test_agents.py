import argparse
import asyncio
import sys
from agents import BaseAgent, AgentEventType

async def test_agent() -> None:
    parser = argparse.ArgumentParser(description="Nexus v2 Chat CLI")
    parser.add_argument("prompt", nargs="?", help="Input prompt for the Agent")
    args, _ = parser.parse_known_args()

    input_prompt = args.prompt or "Hello, agent!"

    async with BaseAgent() as agent:
        try:
            async for event in agent.run(input_prompt):
                if event.type == AgentEventType.TEXT_DELTA:
                    content = event.data.get("content", "")
                    print(content, end="", flush=True)

                elif event.type == AgentEventType.TEXT_COMPLETE:
                    print()
                    final_response = event.data.get("content")
                    print(f" Final Response: {final_response}", file=sys.stderr)

                elif event.type == AgentEventType.AGENT_ERROR:
                    print()
                    error = event.data.get("error")
                    print(f"Error: {error}", file=sys.stderr)

        except Exception as e:
            print(f"Exception: {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(test_agent())

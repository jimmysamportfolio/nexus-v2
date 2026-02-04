import argparse
import asyncio
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import config
from llm import LLMClient, StreamEventType

async def test_llm_client():
    parser = argparse.ArgumentParser(description="Nexus v2 Chat CLI")
    parser.add_argument("prompt", nargs="?", help="Input prompt for the AI")
    args, _ = parser.parse_known_args()

    input_prompt = args.prompt or config.DEFAULT_PROMPT

    client = LLMClient()
    messages = [{"role": "user", "content": input_prompt}]

    try:
        async for event in client.chat_completion(messages=messages, stream=True):
            if event.type == StreamEventType.TEXT_DELTA and event.text_delta:
                print(event.text_delta.content, end="", flush=True)
            elif event.type == StreamEventType.MESSAGE_COMPLETE:
                print()  
                if event.usage:
                    print(f"Usage: {event.usage}")
            elif event.type == StreamEventType.ERROR:
                print(f"Error: {event.error}", file=sys.stderr)

    except Exception as e:
        print(f"Exception: {e}", file=sys.stderr)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_llm_client())

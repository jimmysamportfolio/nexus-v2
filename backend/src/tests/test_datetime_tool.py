import asyncio
import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import DateTimeTool
from tools.tool_types import ToolInvocation


async def test_datetime_tool():
    tool = DateTimeTool()

    print("=" * 60)
    print("DateTimeTool Verification")
    print("=" * 60)

    # Test 1: Schema generation
    print("\n1. OpenAI Schema:")
    schema = tool.to_openai_schema()
    print(json.dumps(schema, indent=2))

    # Test 2: now operation
    print("\n2. Test 'now' operation:")
    result = await tool.execute(ToolInvocation(
        cwd=Path.cwd(),
        params={"operation": "now", "timezone": "America/New_York"}
    ))
    print(f"Success: {result.success}")
    print(f"Output:\n{result.output}")

    # Test 3: parse operation
    print("\n3. Test 'parse' operation:")
    result = await tool.execute(ToolInvocation(
        cwd=Path.cwd(),
        params={
            "operation": "parse",
            "datetime_string": "2024-01-15T10:30:00Z"
        }
    ))
    print(f"Success: {result.success}")
    print(f"Output:\n{result.output}")

    # Test 4: format operation
    print("\n4. Test 'format' operation:")
    result = await tool.execute(ToolInvocation(
        cwd=Path.cwd(),
        params={
            "operation": "format",
            "timestamp": "2024-01-15T10:30:00Z",
            "format_string": "%B %d, %Y at %I:%M %p"
        }
    ))
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")

    # Test 5: add operation
    print("\n5. Test 'add' operation:")
    result = await tool.execute(ToolInvocation(
        cwd=Path.cwd(),
        params={
            "operation": "add",
            "timestamp": "2024-01-15T10:30:00Z",
            "days": 7,
            "hours": 2
        }
    ))
    print(f"Success: {result.success}")
    print(f"Output:\n{result.output}")

    # Test 6: diff operation
    print("\n6. Test 'diff' operation:")
    result = await tool.execute(ToolInvocation(
        cwd=Path.cwd(),
        params={
            "operation": "diff",
            "start": "2024-01-15T10:30:00Z",
            "end": "2024-01-20T14:45:30Z"
        }
    ))
    print(f"Success: {result.success}")
    print(f"Output:\n{result.output}")

    # Test 7: Negative diff (end < start)
    print("\n7. Test 'diff' with negative result (end before start):")
    result = await tool.execute(ToolInvocation(
        cwd=Path.cwd(),
        params={
            "operation": "diff",
            "start": "2024-01-20T14:45:30Z",
            "end": "2024-01-15T10:30:00Z"
        }
    ))
    print(f"Success: {result.success}")
    print(f"Output:\n{result.output}")

    # Test 8: Error case
    print("\n8. Test error handling (missing required param):")
    result = await tool.execute(ToolInvocation(
        cwd=Path.cwd(),
        params={"operation": "format"}
    ))
    print(f"Success: {result.success}")
    print(f"Error: {result.error}")

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_datetime_tool())

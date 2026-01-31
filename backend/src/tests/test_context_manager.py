import asyncio
from src.context import ContextManager

def test_context_manager():
    print("Testing ContextManager...")
    ctx = ContextManager()
    
    # Test adding messages
    ctx.add_message("user", "Hello")
    ctx.add_message("assistant", "Hi there")
    
    messages = ctx.get_messages()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there"
    print("Add message/Get messages: OK")

    # Test get last message
    last = ctx.get_last_message()
    assert last is not None
    assert last["content"] == "Hi there"
    print("Get last message: OK")

    ctx.clear()
    assert len(ctx.get_messages()) == 0
    assert ctx.get_last_message() is None
    print("Clear: OK")

    # Test add error
    ctx.add_error("Something went wrong")
    last = ctx.get_last_message()
    assert last is not None
    assert last["role"] == "system"
    assert "Error: Something went wrong" in last["content"]
    print("Add error: OK")

if __name__ == "__main__":
    test_context_manager()

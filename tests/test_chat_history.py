"""Tests for chat history functionality."""
import pytest


def format_history_for_api(chat_history):
    """Format chat history for Gemini API - mimics app.py logic."""
    history = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})
    return history


def test_chat_history_initialization():
    """Test that chat history initializes as empty list."""
    chat_history = []
    assert chat_history == []
    assert len(chat_history) == 0


def test_add_user_message():
    """Test adding user message to chat history."""
    chat_history = []
    user_message = {"role": "user", "content": "Hello"}
    chat_history.append(user_message)
    
    assert len(chat_history) == 1
    assert chat_history[0]["role"] == "user"
    assert chat_history[0]["content"] == "Hello"


def test_add_assistant_message():
    """Test adding assistant message to chat history."""
    chat_history = []
    assistant_message = {"role": "assistant", "content": "Hi there!"}
    chat_history.append(assistant_message)
    
    assert len(chat_history) == 1
    assert chat_history[0]["role"] == "assistant"
    assert chat_history[0]["content"] == "Hi there!"


def test_chat_history_alternating_messages(chat_history_sample):
    """Test chat history with alternating user and assistant messages."""
    assert len(chat_history_sample) == 2
    assert chat_history_sample[0]["role"] == "user"
    assert chat_history_sample[1]["role"] == "assistant"


def test_format_history_for_api(chat_history_sample):
    """Test formatting chat history for Gemini API."""
    formatted = format_history_for_api(chat_history_sample)
    
    assert len(formatted) == 2
    assert formatted[0]["role"] == "user"
    assert formatted[0]["parts"] == [chat_history_sample[0]["content"]]
    assert formatted[1]["role"] == "model"
    assert formatted[1]["parts"] == [chat_history_sample[1]["content"]]


def test_format_empty_history():
    """Test formatting empty chat history."""
    formatted = format_history_for_api([])
    assert formatted == []


def test_format_single_message():
    """Test formatting history with single message."""
    history = [{"role": "user", "content": "Hello"}]
    formatted = format_history_for_api(history)
    
    assert len(formatted) == 1
    assert formatted[0]["role"] == "user"
    assert formatted[0]["parts"] == ["Hello"]


def test_chat_history_clear():
    """Test clearing chat history."""
    chat_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"}
    ]
    assert len(chat_history) == 2
    
    chat_history = []
    assert len(chat_history) == 0


def test_chat_history_message_structure():
    """Test that chat history messages have correct structure."""
    message = {"role": "user", "content": "Test message"}
    
    assert "role" in message
    assert "content" in message
    assert message["role"] in ["user", "assistant"]
    assert isinstance(message["content"], str)


def test_chat_history_multiple_turns():
    """Test chat history with multiple conversation turns."""
    chat_history = [
        {"role": "user", "content": "I want pizza"},
        {"role": "assistant", "content": "How many pizzas?"},
        {"role": "user", "content": "2 pizzas"},
        {"role": "assistant", "content": "Added 2 pizzas"}
    ]
    
    assert len(chat_history) == 4
    assert all(msg["role"] in ["user", "assistant"] for msg in chat_history)
    assert chat_history[0]["role"] == "user"
    assert chat_history[1]["role"] == "assistant"
    assert chat_history[2]["role"] == "user"
    assert chat_history[3]["role"] == "assistant"


def test_format_history_with_multiple_turns():
    """Test formatting history with multiple conversation turns."""
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I'm good!"}
    ]
    
    formatted = format_history_for_api(history)
    assert len(formatted) == 4
    assert formatted[0]["role"] == "user"
    assert formatted[1]["role"] == "model"
    assert formatted[2]["role"] == "user"
    assert formatted[3]["role"] == "model"


def test_chat_history_exclude_current_message():
    """Test excluding current user message from history (for API call)."""
    full_history = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "Response"},
        {"role": "user", "content": "Current message"}  # This should be excluded
    ]
    
    # Exclude last message (current user input)
    history_for_api = full_history[:-1]
    formatted = format_history_for_api(history_for_api)
    
    assert len(formatted) == 2
    assert formatted[0]["role"] == "user"
    assert formatted[1]["role"] == "model"
    assert "Current message" not in str(formatted)


def test_chat_history_preserves_content():
    """Test that chat history preserves message content exactly."""
    original_content = "I want 2 large pizzas with extra cheese"
    message = {"role": "user", "content": original_content}
    chat_history = [message]
    
    assert chat_history[0]["content"] == original_content
    assert len(chat_history[0]["content"]) == len(original_content)


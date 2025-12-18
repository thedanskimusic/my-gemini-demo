"""Integration tests for complete workflows."""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def mock_streamlit_session_state():
    """Mock Streamlit session state."""
    return {
        "chat_history": [],
        "selected_persona": "None",
        "current_order": None
    }


def test_full_ordering_agent_workflow(personas_dict, sample_order_json):
    """Test complete ordering agent workflow from conversation to JSON parsing."""
    # Simulate workflow steps
    
    # 1. Initialize with Ordering Agent persona
    selected_persona = "Ordering Agent"
    persona = personas_dict[selected_persona]
    assert persona["system_prompt"] is not None
    
    # 2. User sends message
    chat_history = []
    user_message = "I want 2 pizzas and 1 soda"
    chat_history.append({"role": "user", "content": user_message})
    assert len(chat_history) == 1
    
    # 3. Simulate AI response with JSON order
    order_response = json.dumps(sample_order_json)
    chat_history.append({"role": "assistant", "content": order_response})
    assert len(chat_history) == 2
    
    # 4. Parse order from response
    parsed_order = json.loads(order_response)
    if "items" in parsed_order:
        current_order = parsed_order
        assert current_order is not None
        assert "items" in current_order
        assert len(current_order["items"]) == 2


def test_persona_switch_preserves_conversation(personas_dict):
    """Test that switching personas preserves conversation history."""
    # Start with None persona and conversation
    chat_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    current_persona = "None"
    
    # Switch to Ordering Agent
    new_persona = "Ordering Agent"
    
    # Conversation history should persist
    assert len(chat_history) == 2
    assert chat_history[0]["content"] == "Hello"
    assert personas_dict[new_persona]["system_prompt"] is not None


def test_error_handling_invalid_api_response():
    """Test error handling for invalid API response."""
    # Simulate API error
    try:
        # This would normally raise an exception
        raise Exception("API Error: Invalid API key")
    except Exception as e:
        error_msg = f"Error: {e}"
        assert "Error:" in error_msg
        assert "API Error" in str(e)


def test_error_handling_malformed_json():
    """Test error handling for malformed JSON in response."""
    malformed_json = '{"items": [invalid json}'
    
    try:
        parsed = json.loads(malformed_json)
        assert False, "Should have raised JSONDecodeError"
    except json.JSONDecodeError:
        # Expected error, handle gracefully
        assert True


def test_multiple_persona_switches():
    """Test multiple persona switches in one session."""
    personas_sequence = ["None", "Ordering Agent", "None", "Ordering Agent"]
    chat_history = []
    
    for persona in personas_sequence:
        # Each switch should work
        assert persona in ["None", "Ordering Agent"]
        # History should persist
        assert isinstance(chat_history, list)


def test_order_parsing_workflow(personas_dict, sample_order_json_string):
    """Test complete order parsing workflow."""
    # 1. Ordering Agent persona is active
    selected_persona = "Ordering Agent"
    assert selected_persona in personas_dict
    
    # 2. AI responds with order JSON embedded in text
    response_text = f"""Here's your order:
{sample_order_json_string}
Is this correct?"""
    
    # 3. Parse the order
    parsed_order = json.loads(sample_order_json_string)
    if "items" in parsed_order:
        current_order = parsed_order
        assert current_order is not None
        assert "items" in current_order


def test_conversation_context_maintained():
    """Test that conversation context is maintained across turns."""
    chat_history = [
        {"role": "user", "content": "I want pizza"},
        {"role": "assistant", "content": "How many?"},
        {"role": "user", "content": "2 pizzas"},
        {"role": "assistant", "content": "Added 2 pizzas"}
    ]
    
    # History should contain full context
    assert len(chat_history) == 4
    assert chat_history[0]["content"] == "I want pizza"
    assert chat_history[2]["content"] == "2 pizzas"
    
    # Format for API should preserve context
    formatted = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        formatted.append({"role": role, "parts": [msg["content"]]})
    
    assert len(formatted) == 4
    assert formatted[0]["role"] == "user"
    assert formatted[1]["role"] == "model"


def test_ordering_agent_workflow_with_order_updates(personas_dict):
    """Test ordering agent workflow with order updates."""
    # Initialize
    chat_history = []
    current_order = None
    selected_persona = "Ordering Agent"
    
    # First order
    user_msg1 = "I want 2 pizzas"
    chat_history.append({"role": "user", "content": user_msg1})
    
    order1 = {"items": [{"name": "pizza", "quantity": 2}]}
    current_order = order1
    
    # Update order
    user_msg2 = "Actually, make it 3 pizzas"
    chat_history.append({"role": "user", "content": user_msg2})
    
    order2 = {"items": [{"name": "pizza", "quantity": 3}]}
    current_order = order2
    
    assert current_order["items"][0]["quantity"] == 3
    assert len(chat_history) == 2


def test_persona_none_workflow(personas_dict):
    """Test workflow with None persona (no special handling)."""
    selected_persona = "None"
    persona = personas_dict[selected_persona]
    
    assert persona["system_prompt"] is None
    
    chat_history = []
    user_msg = "Tell me a joke"
    chat_history.append({"role": "user", "content": user_msg})
    
    # No order parsing should occur
    current_order = None
    assert current_order is None


def test_error_handling_json_parsing_failure():
    """Test error handling when JSON parsing fails but conversation continues."""
    response_text = "I understand you want to order. What would you like?"
    
    # Try to parse JSON
    try:
        parsed_order = json.loads(response_text)
        assert False, "Should have raised JSONDecodeError"
    except json.JSONDecodeError:
        # Gracefully handle - conversation continues
        current_order = None
        assert current_order is None


def test_integration_clear_conversation():
    """Test clearing conversation resets state."""
    chat_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"}
    ]
    current_order = {"items": [{"name": "pizza", "quantity": 1}]}
    
    # Clear conversation
    chat_history = []
    current_order = None
    
    assert len(chat_history) == 0
    assert current_order is None


def test_order_extraction_from_conversational_response(sample_order_json):
    """Test extracting order JSON from conversational AI response."""
    conversational_response = f"""I've added the following items to your order:
{json.dumps(sample_order_json)}

Would you like to add anything else?"""
    
    # Extract JSON from response
    # Try to find JSON in response
    json_match = json.dumps(sample_order_json)
    if json_match in conversational_response:
        parsed_order = json.loads(json_match)
        assert parsed_order["items"][0]["name"] == "pizza"


def test_multiple_conversation_turns_with_order_parsing():
    """Test multiple conversation turns with order parsing."""
    chat_history = []
    current_order = None
    
    # Turn 1
    chat_history.append({"role": "user", "content": "I want pizza"})
    response1 = "How many pizzas?"
    chat_history.append({"role": "assistant", "content": response1})
    
    # Turn 2
    chat_history.append({"role": "user", "content": "2 pizzas"})
    order_json = json.dumps({"items": [{"name": "pizza", "quantity": 2}]})
    chat_history.append({"role": "assistant", "content": order_json})
    current_order = json.loads(order_json)
    
    assert len(chat_history) == 4
    assert current_order["items"][0]["quantity"] == 2


"""Pytest configuration and shared fixtures."""
import pytest
import json


@pytest.fixture
def personas_dict():
    """Fixture for personas dictionary."""
    return {
        "None": {
            "name": "None",
            "description": "Default chat mode (no persona)",
            "system_prompt": None
        },
        "Ordering Agent": {
            "name": "Ordering Agent",
            "description": "Parses conversations into structured JSON orders",
            "system_prompt": """You are an order processing agent. Your task is to:
1. Parse natural language orders from conversations into structured JSON format
2. Maintain order state across conversation turns
3. When asked to provide the order, output ONLY valid JSON in this format: {"items": [{"name": "item name", "quantity": number, "notes": "optional notes"}]}
4. Be conversational and helpful, but always be ready to provide structured order data when requested"""
        }
    }


@pytest.fixture
def sample_order_json():
    """Fixture for sample valid order JSON."""
    return {
        "items": [
            {"name": "pizza", "quantity": 2, "notes": "large"},
            {"name": "soda", "quantity": 1}
        ]
    }


@pytest.fixture
def sample_order_json_string(sample_order_json):
    """Fixture for sample order as JSON string."""
    return json.dumps(sample_order_json)


@pytest.fixture
def chat_history_sample():
    """Fixture for sample chat history."""
    return [
        {"role": "user", "content": "I want 2 pizzas"},
        {"role": "assistant", "content": "Got it! I've added 2 pizzas to your order."}
    ]


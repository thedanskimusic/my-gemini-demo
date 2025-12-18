"""Tests for order parsing logic."""
import pytest
import json
import re


def parse_order_json(response_text):
    """Extract order JSON from response text - mimics app.py logic."""
    try:
        # Try to parse the entire response as JSON first
        parsed_order = json.loads(response_text)
        if "items" in parsed_order:
            return parsed_order
    except json.JSONDecodeError:
        # Try to extract JSON from response using regex
        try:
            # Match JSON object with "items" key (handles nested structures)
            json_match = re.search(r'\{[^{}]*"items"[^{}]*\[.*?\][^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_order = json.loads(json_str)
                if "items" in parsed_order:
                    return parsed_order
        except (json.JSONDecodeError, AttributeError):
            # Not JSON, that's okay
            return None
    return None


def test_parse_valid_json_order(sample_order_json_string):
    """Test parsing valid JSON order from pure JSON string."""
    result = parse_order_json(sample_order_json_string)
    assert result is not None
    assert "items" in result
    assert len(result["items"]) == 2
    assert result["items"][0]["name"] == "pizza"


def test_parse_json_in_text_response(sample_order_json):
    """Test parsing JSON order from text containing JSON."""
    response_text = f"""Here's your order:
{json.dumps(sample_order_json)}
Is that correct?"""
    
    result = parse_order_json(response_text)
    assert result is not None
    assert "items" in result
    assert len(result["items"]) == 2


def test_parse_json_with_conversation(sample_order_json):
    """Test parsing JSON from conversational response."""
    response_text = f"""I've added the following items to your order:
{json.dumps(sample_order_json)}

Would you like to add anything else?"""
    
    result = parse_order_json(response_text)
    assert result is not None
    assert result["items"][0]["name"] == "pizza"


def test_parse_invalid_json():
    """Test parsing invalid JSON."""
    invalid_json = '{"items": [invalid]}'
    result = parse_order_json(invalid_json)
    # Should handle gracefully and return None
    assert result is None or "items" not in result


def test_parse_json_without_items_key():
    """Test parsing JSON that doesn't have items key."""
    json_without_items = '{"order_id": 123, "total": 25.50}'
    result = parse_order_json(json_without_items)
    # Should return None since "items" key is required
    assert result is None


def test_parse_empty_order():
    """Test parsing empty order."""
    empty_order = {"items": []}
    result = parse_order_json(json.dumps(empty_order))
    assert result is not None
    assert "items" in result
    assert len(result["items"]) == 0


def test_parse_order_with_missing_fields():
    """Test parsing order with missing optional fields."""
    order_missing_fields = {
        "items": [
            {"name": "pizza", "quantity": 2},
            {"name": "soda"}  # missing quantity
        ]
    }
    result = parse_order_json(json.dumps(order_missing_fields))
    assert result is not None
    assert len(result["items"]) == 2
    assert result["items"][0]["name"] == "pizza"
    assert result["items"][1]["name"] == "soda"


def test_parse_order_with_notes(sample_order_json):
    """Test parsing order with notes field."""
    result = parse_order_json(json.dumps(sample_order_json))
    assert result is not None
    assert result["items"][0].get("notes") == "large"
    assert result["items"][1].get("notes") is None or "notes" not in result["items"][1]


def test_parse_non_json_text():
    """Test parsing non-JSON text."""
    plain_text = "I understand you want to place an order. What would you like?"
    result = parse_order_json(plain_text)
    # Should return None for non-JSON text
    assert result is None


def test_parse_multiple_json_objects():
    """Test parsing when multiple JSON objects exist in text."""
    text_with_multiple_json = f"""First: {{"not": "order"}}
Second: {json.dumps({"items": [{"name": "pizza", "quantity": 1}]})}"""
    
    result = parse_order_json(text_with_multiple_json)
    # Should extract the one with "items" key
    assert result is not None
    assert "items" in result


def test_parse_nested_json_structure():
    """Test parsing nested JSON structures."""
    nested_order = {
        "items": [
            {
                "name": "pizza",
                "quantity": 2,
                "notes": "with extra cheese",
                "toppings": ["pepperoni", "mushrooms"]
            }
        ]
    }
    result = parse_order_json(json.dumps(nested_order))
    assert result is not None
    assert result["items"][0]["toppings"] == ["pepperoni", "mushrooms"]


def test_parse_order_preserves_data_types():
    """Test that order parsing preserves correct data types."""
    order_with_types = {
        "items": [
            {"name": "pizza", "quantity": 2, "price": 12.99}
        ]
    }
    result = parse_order_json(json.dumps(order_with_types))
    assert result is not None
    assert isinstance(result["items"][0]["quantity"], int)
    assert isinstance(result["items"][0]["price"], float)


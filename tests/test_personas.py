"""Tests for persona system."""
import pytest


def test_personas_structure(personas_dict):
    """Test that personas dictionary has correct structure."""
    # Should have required keys
    assert "None" in personas_dict
    assert "Ordering Agent" in personas_dict
    
    # Each persona should have required fields
    for persona_name, persona_data in personas_dict.items():
        assert "name" in persona_data
        assert "description" in persona_data
        assert "system_prompt" in persona_data
        assert persona_data["name"] == persona_name


def test_none_persona(personas_dict):
    """Test that None persona has no system prompt."""
    none_persona = personas_dict["None"]
    assert none_persona["system_prompt"] is None
    assert none_persona["description"] == "Default chat mode (no persona)"


def test_ordering_agent_persona(personas_dict):
    """Test that Ordering Agent persona has system prompt."""
    ordering_agent = personas_dict["Ordering Agent"]
    assert ordering_agent["system_prompt"] is not None
    assert len(ordering_agent["system_prompt"]) > 0
    assert "order processing agent" in ordering_agent["system_prompt"].lower()
    assert "json" in ordering_agent["system_prompt"].lower()
    assert ordering_agent["description"] == "Parses conversations into structured JSON orders"


def test_persona_switching(personas_dict):
    """Test persona switching logic."""
    # Simulate switching from None to Ordering Agent
    current_persona = "None"
    new_persona = "Ordering Agent"
    
    assert current_persona != new_persona
    assert personas_dict[current_persona]["system_prompt"] is None
    assert personas_dict[new_persona]["system_prompt"] is not None
    
    # After switching
    current_persona = new_persona
    assert personas_dict[current_persona]["system_prompt"] is not None


def test_system_prompt_application(personas_dict):
    """Test that system prompts are correctly applied."""
    # None persona should return None
    none_prompt = personas_dict["None"]["system_prompt"]
    assert none_prompt is None
    
    # Ordering Agent should return a prompt string
    ordering_prompt = personas_dict["Ordering Agent"]["system_prompt"]
    assert ordering_prompt is not None
    assert isinstance(ordering_prompt, str)


def test_persona_descriptions_exist(personas_dict):
    """Test that all personas have descriptions."""
    for persona_name, persona_data in personas_dict.items():
        assert "description" in persona_data
        assert persona_data["description"] is not None
        assert len(persona_data["description"]) > 0


def test_personas_extensible_structure(personas_dict):
    """Test that persona structure allows easy extension."""
    # New persona can be added with same structure
    new_persona = {
        "name": "Test Persona",
        "description": "A test persona",
        "system_prompt": "You are a test persona."
    }
    
    # Verify structure matches
    required_keys = {"name", "description", "system_prompt"}
    assert set(new_persona.keys()) == required_keys
    
    # All required keys should be in existing personas
    for persona_data in personas_dict.values():
        assert set(persona_data.keys()) == required_keys


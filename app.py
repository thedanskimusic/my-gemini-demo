import streamlit as st
import google.generativeai as genai
import json
import re

# Streamlit looks into .streamlit/secrets.toml automatically
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# Define personas
PERSONAS = {
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

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_persona" not in st.session_state:
    st.session_state.selected_persona = "None"
if "current_order" not in st.session_state:
    st.session_state.current_order = None

# Get available model
@st.cache_resource
def get_model():
    try:
        models = genai.list_models()
        available_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name.replace('models/', ''))
        if available_models:
            return available_models[0], None
        else:
            return None, "No models found that support generateContent"
    except Exception as e:
        return None, str(e)

model_name, model_error = get_model()

# Title
st.title("Gemini Demo")

# Persona selector
st.subheader("Persona")
selected_persona = st.selectbox(
    "Choose a persona:",
    options=list(PERSONAS.keys()),
    index=list(PERSONAS.keys()).index(st.session_state.selected_persona),
    key="persona_selector"
)

if selected_persona != st.session_state.selected_persona:
    st.session_state.selected_persona = selected_persona

# Show persona description
if PERSONAS[selected_persona]["description"]:
    st.caption(PERSONAS[selected_persona]["description"])

# Show available models (for debugging)
with st.expander("Available Models"):
    if model_error:
        st.error(f"Error: {model_error}")
    elif model_name:
        st.info(f"Using model: {model_name}")
        try:
            models = genai.list_models()
            available_models = []
            for m in models:
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name.replace('models/', ''))
            st.write("Models that support generateContent:")
            for m_name in available_models:
                st.write(f"- {m_name}")
        except Exception as e:
            st.error(f"Error listing models: {e}")
    else:
        st.error("No model available")

# Display chat history
st.subheader("Conversation")
if st.session_state.chat_history:
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        with st.chat_message(role):
            st.write(content)
else:
    st.info("Start a conversation below...")

# Show current order if ordering agent is active
if selected_persona == "Ordering Agent" and st.session_state.current_order:
    st.subheader("Current Order")
    st.json(st.session_state.current_order)

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input and model_name:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Get persona system prompt
    persona = PERSONAS[selected_persona]
    system_prompt = persona["system_prompt"]
    
    # Prepare model with system instruction if persona has one
    if system_prompt:
        model = genai.GenerativeModel(model_name, system_instruction=system_prompt)
    else:
        model = genai.GenerativeModel(model_name)
    
    # Generate response
    with st.spinner("Generating response..."):
        with st.chat_message("assistant"):
            try:
                # Use chat history for context
                if len(st.session_state.chat_history) > 1:
                    # Prepare history for chat (exclude the current user message we just added)
                    history = []
                    for msg in st.session_state.chat_history[:-1]:
                        role = "user" if msg["role"] == "user" else "model"
                        history.append({"role": role, "parts": [msg["content"]]})
                    
                    # Start chat session with history
                    chat = model.start_chat(history=history)
                    response = chat.send_message(user_input)
                else:
                    # First message, no history
                    response = model.generate_content(user_input)
                
                response_text = response.text
                st.write(response_text)
                
                # Add assistant response to history
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
                # Try to parse JSON order if ordering agent is active
                if selected_persona == "Ordering Agent":
                    try:
                        # Try to parse the entire response as JSON first
                        parsed_order = json.loads(response_text)
                        if "items" in parsed_order:
                            st.session_state.current_order = parsed_order
                    except json.JSONDecodeError:
                        # Try to extract JSON from response using regex
                        try:
                            # Match JSON object with "items" key (handles nested structures)
                            json_match = re.search(r'\{[^{}]*"items"[^{}]*\[.*?\][^{}]*\}', response_text, re.DOTALL)
                            if json_match:
                                json_str = json_match.group(0)
                                parsed_order = json.loads(json_str)
                                if "items" in parsed_order:
                                    st.session_state.current_order = parsed_order
                        except (json.JSONDecodeError, AttributeError):
                            # Not JSON, that's okay - will update on next turn
                            pass
                        
            except Exception as e:
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# Clear conversation button
if st.button("Clear Conversation"):
    st.session_state.chat_history = []
    st.session_state.current_order = None
    st.rerun()

import streamlit as st
import google.generativeai as genai

# Streamlit looks into .streamlit/secrets.toml automatically
api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

# List available models and find one that supports generateContent
st.title("Gemini Demo")

# Show available models (for debugging)
with st.expander("Available Models"):
    try:
        models = genai.list_models()
        available_models = []
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name.replace('models/', ''))
        st.write("Models that support generateContent:")
        for model_name in available_models:
            st.write(f"- {model_name}")
        
        # Use the first available model
        if available_models:
            model_name = available_models[0]
            st.info(f"Using model: {model_name}")
            model = genai.GenerativeModel(model_name)
        else:
            st.error("No models found that support generateContent")
            model = None
    except Exception as e:
        st.error(f"Error listing models: {e}")
        model = None

user_input = st.text_input("Ask me anything:")

if user_input and model:
    with st.spinner("Generating response..."):
        try:
            response = model.generate_content(user_input)
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {e}")


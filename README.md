# Gemini Demo

A Streamlit application showcasing Google's Gemini LLM integration.

## Setup

1. Create virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   To deactivate: `deactivate`

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your API key:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Edit `.streamlit/secrets.toml` and replace `your_actual_key_from_google_ai_studio` with your actual key

4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Deploying to Streamlit Cloud

1. Push your code to GitHub (the `.gitignore` file ensures your secrets.toml is not uploaded)

2. Connect your repository to [Streamlit Community Cloud](https://streamlit.io/cloud)

3. In the "Advanced Settings" on the Streamlit dashboard, paste the contents of your `.streamlit/secrets.toml` into the Secrets box

## Security Note

Never commit your `.streamlit/secrets.toml` file to version control. It's already included in `.gitignore` for your protection.


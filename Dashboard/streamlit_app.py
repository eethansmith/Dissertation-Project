import streamlit as st
from openai import OpenAI

# Streamlit App title
st.title("Efficacy of Guardrails for Large Language Models Dashboard")

# Model options (example models; feel free to customize)
MODEL_OPTIONS = [
    "openai/gpt-3.5-turbo",
    "openai/gpt-4o-mini",
    "google/gemini-pro",
    "anthropic/claude-3-haiku",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3-8b-instruct"
]

# Set your OpenRouter API key securely via Streamlit secrets
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

def query_openrouter(model, prompt):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            extra_headers={
                "HTTP-Referer": "https://yourwebsite.com",  # Replace with your site URL (optional)
                "X-Title": "Efficacy of Guardrails for Large Language Models Dashboard"         # Replace with your site name/title (optional)
            }
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# Streamlit Interface
selected_model = st.selectbox("Select LLM Model:", MODEL_OPTIONS)
user_prompt = st.text_area("Your Prompt:", height=200)

if st.button("Submit"):
    if user_prompt.strip():
        with st.spinner(f"Querying {selected_model}..."):
            response = query_openrouter(selected_model, user_prompt)
            if response:
                st.subheader("Response:")
                st.write(response)
    else:
        st.error("Please enter a prompt.")

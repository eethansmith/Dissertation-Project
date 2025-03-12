import streamlit as st
from openai import OpenAI

# Initialize OpenRouter API
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

MODEL_OPTIONS = [
    "openai/gpt-3.5-turbo",
    "openai/gpt-4",
    "google/gemini-pro",
    "anthropic/claude-2",
    "meta-llama/llama-3-8b-instruct"
]

def query_model(prompt, model):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    if response and response.choices:
        return response.choices[0].message.content
    else:
        return None

# Streamlit UI
st.title("LLM Efficacy Dashboard")

selected_model = st.selectbox("Choose a Large Language Model:", MODEL_OPTIONS)

user_input = st.text_area("Enter your prompt:", height=200)

if st.button("Evaluate"):
    if user_input.strip():
        with st.spinner(f"Querying {selected_model}..."):
            try:
                response = query_model(user_input, selected_model)
                if response:
                    st.markdown("### Response")
                    st.write(response)
                else:
                    st.error("No response received. Please check your prompt or model.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a prompt to evaluate.")

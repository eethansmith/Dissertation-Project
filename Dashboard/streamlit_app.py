import streamlit as st
import os
import pandas as pd
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
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# List available CSV files in "TestScripts" directory
test_scripts_dir = "TestScripts"
os.makedirs(test_scripts_dir, exist_ok=True)  # Ensure directory exists
csv_files = [f for f in os.listdir(test_scripts_dir) if f.endswith(".csv")]

# Allow user to upload their own CSV
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])

if uploaded_file:
    uploaded_filename = os.path.join(test_scripts_dir, uploaded_file.name)
    with open(uploaded_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    csv_files.append(uploaded_file.name)  # Add uploaded file to dropdown options

# Dropdown to select CSV file
selected_csv = st.selectbox("Select a CSV file for testing:", csv_files)

# Display selected CSV content
if selected_csv:
    csv_path = os.path.join(test_scripts_dir, selected_csv)
    df = pd.read_csv(csv_path)
    st.write(f"### Preview of {selected_csv}")
    st.dataframe(df)

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

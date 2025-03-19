import streamlit as st
import os
import pandas as pd
import time
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

def query_openrouter(model, system_prompt, user_prompt):
    """Sends system and user prompts to the model and retrieves the response."""
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"API Error: {e}"

# Ensure directory exists
test_scripts_dir = "TestScripts"
os.makedirs(test_scripts_dir, exist_ok=True)

# List CSV files in directory
csv_files = [f for f in os.listdir(test_scripts_dir) if f.endswith(".csv")]

# File uploader for new CSVs
uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
if uploaded_file:
    uploaded_filename = os.path.join(test_scripts_dir, uploaded_file.name)
    with open(uploaded_filename, "wb") as f:
        f.write(uploaded_file.getbuffer())
    csv_files.append(uploaded_file.name)  # Add uploaded file to dropdown

# Dropdown to select CSV
selected_csv = st.selectbox("Select a CSV file for testing:", csv_files)

# Dropdown for model selection
selected_model = st.selectbox("Select LLM Model:", MODEL_OPTIONS)

if st.button("Start Testing"):
    if selected_csv:
        csv_path = os.path.join(test_scripts_dir, selected_csv)
        df = pd.read_csv(csv_path)

        # Ensure required columns exist
        required_columns = {"System Prompt", "User Prompt", "Detected"}
        if not required_columns.issubset(df.columns):
            st.error("Selected CSV does not contain the required columns: 'System Prompt', 'User Prompt', 'Detected'")
        else:
            st.write("### Running Tests...")
            results = []

            for _, row in df.iterrows():
                system_prompt = str(row["System Prompt"])
                user_prompt = str(row["User Prompt"])
                detected_words = str(row["Detected"]).split(",")  # Convert to list
                detected_words = [word.strip().lower() for word in detected_words]  # Normalize case & spacing

                with st.spinner(f"Querying model for prompt: {user_prompt[:30]}..."):
                    response = query_openrouter(selected_model, system_prompt, user_prompt)

                    # Check if any detected words appear in the response
                    leaked_words = [word for word in detected_words if word in response.lower()]
                    leak_status = 1 if leaked_words else 0  # 1 if leaked, else 0
                    
                    results.append({
                        "Model": selected_model,
                        "User Prompt": user_prompt,
                        "Leaked Words": ", ".join(leaked_words) if leaked_words else "None",
                        "Leak": leak_status  # 0 = No Leak, 1 = Leak
                    })
                    
            # Display Results
            results_df = pd.DataFrame(results)

    else:
        st.error("Please select a CSV file for testing.")

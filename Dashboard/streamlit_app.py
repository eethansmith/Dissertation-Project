import streamlit as st
import os
import pandas as pd
import time
from openai import OpenAI

# Constants
MODEL_OPTIONS = [
    "openai/gpt-3.5-turbo",
    "openai/gpt-4o-mini",
    "google/gemini-pro",
    "anthropic/claude-3-haiku",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3-8b-instruct"
]

TEST_SCRIPTS_DIR = "TestScripts"
os.makedirs(TEST_SCRIPTS_DIR, exist_ok=True)  # Ensure directory exists


class GuardrailsTester:
    """Class to handle guardrail testing for Large Language Models."""
    
    def __init__(self):
        """Initialize the API client and fetch available CSV files."""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=st.secrets["OPENROUTER_API_KEY"]
        )
        self.csv_files = self.get_csv_files()
    
    def get_csv_files(self):
        """Fetch available CSV files in the test scripts directory."""
        return [f for f in os.listdir(TEST_SCRIPTS_DIR) if f.endswith(".csv")]
    
    def upload_file(self):
        """Handle file upload and add it to available CSVs."""
        uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
        if uploaded_file:
            uploaded_filename = os.path.join(TEST_SCRIPTS_DIR, uploaded_file.name)
            with open(uploaded_filename, "wb") as f:
                f.write(uploaded_file.getbuffer())
            self.csv_files.append(uploaded_file.name)
            st.success(f"Uploaded {uploaded_file.name}")
    
    def query_openrouter(self, model, system_prompt, user_prompt):
        """Query the OpenRouter API and return response with timing."""
        start_time = time.time()
        
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            )
            response = completion.choices[0].message.content
        except Exception as e:
            response = f"API Error: {e}"
        
        response_time = round(time.time() - start_time, 3)  # Compute response time
        return response, response_time
    
    def process_csv(self, selected_csv, selected_model):
        """Process the selected CSV, run tests, and display results."""
        csv_path = os.path.join(TEST_SCRIPTS_DIR, selected_csv)
        df = pd.read_csv(csv_path)

        required_columns = {"System Prompt", "User Prompt", "Detected"}
        if not required_columns.issubset(df.columns):
            st.error("CSV missing required columns: 'System Prompt', 'User Prompt', 'Detected'")
            return
        
        st.write("### Running Tests...")
        results = []

        for _, row in df.iterrows():
            system_prompt = str(row["System Prompt"])
            user_prompt = str(row["User Prompt"])
            detected_words = [word.strip().lower() for word in str(row["Detected"]).split(",")]

            with st.spinner(f"Querying model for prompt: {user_prompt[:30]}..."):
                response, response_time = self.query_openrouter(selected_model, system_prompt, user_prompt)

                # Detect leaked words
                leaked_words = [word for word in detected_words if word in response.lower()]
                leak_status = 1 if leaked_words else 0
                
                results.append({
                    "Model": selected_model,
                    "User Prompt": user_prompt,
                    "Leaked Words": ", ".join(leaked_words) if leaked_words else "None",
                    "Leak": leak_status,
                    "Response Time (seconds)": response_time
                })

        # Convert results to DataFrame and display
        results_df = pd.DataFrame(results)

        if not results_df.empty:
            st.write("### Test Results (Leaked PII Detected)")
            st.dataframe(results_df)

            # Save results
            results_filename = f"{selected_csv.replace('.csv', '')}-{selected_model.replace('/','-')}-results.csv"
            results_filepath = os.path.join(TEST_SCRIPTS_DIR, results_filename)
            results_df.to_csv(results_filepath, index=False)

            st.success(f"Results saved to: {results_filename}")
            st.download_button(
                label="Download Results CSV",
                data=results_df.to_csv(index=False).encode("utf-8"),
                file_name=results_filename,
                mime="text/csv",
            )
        else:
            st.success("No PII detected in model outputs!")


def main():
    """Main function to run the Streamlit app."""
    st.title("Efficacy of Guardrails for Large Language Models Dashboard")

    # Initialize GuardrailsTester instance
    tester = GuardrailsTester()
    
    # Handle file uploads
    tester.upload_file()
    
    # Dropdowns for CSV and Model Selection
    selected_csv = st.selectbox("Select a CSV file for testing:", tester.csv_files)
    selected_model = st.selectbox("Select LLM Model:", MODEL_OPTIONS)

    # Start Testing Button
    if st.button("Start Testing"):
        if selected_csv:
            tester.process_csv(selected_csv, selected_model)
        else:
            st.error("Please select a CSV file for testing.")
    
    # Load the visualization from the HTML file
    with open("visualization.html", "r", encoding="utf-8") as f:
        html_code = f.read()

    # Render the HTML inside the Streamlit app
    st.components.v1.html(html_code, height=500, scrolling=True)


# Run the Streamlit App
if __name__ == "__main__":
    main()

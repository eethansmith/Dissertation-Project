import streamlit as st
import os
import pandas as pd
import time
from openai import OpenAI

## Guardrails AI Import
from guardrails.hub import DetectPII
from guardrails import Guard

# Lakera Guard Import
from guards.lakera_guard import lakera_pii_check

from guards.guardrails_ai import guardrails_ai_check


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
    
    def process_csv(self, selected_csv, selected_model, use_guardrails=True, use_lakera=False):
        """Process the selected CSV, run tests, and display results."""
        csv_path = os.path.join(TEST_SCRIPTS_DIR, selected_csv)
        df = pd.read_csv(csv_path)

        required_columns = {"System Prompt", "User Prompt", "Detected"}
        if not required_columns.issubset(df.columns):
            st.error("CSV missing required columns: 'System Prompt', 'User Prompt', 'Detected'")
            return
        
        st.write("### Running Tests...")
        results = []

        # Initialize Guardrails
        pii_guard = Guard().use(
            DetectPII, ["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD"], "fix"
        )

        for _, row in df.iterrows():
            system_prompt = str(row["System Prompt"])
            user_prompt = str(row["User Prompt"])
            detected_words = [word.strip().lower() for word in str(row["Detected"]).split(",")]

            with st.spinner(f"Querying model for prompt: {user_prompt[:30]}..."):
                # Query LLM and measure time
                raw_response_start = time.time()
                raw_response, response_time = self.query_openrouter(selected_model, system_prompt, user_prompt)
                raw_response_end = time.time()

                # Check for raw leak
                raw_leaked_words = [word for word in detected_words if word in raw_response.lower()]
                raw_leak_status = 1 if raw_leaked_words else 0

                # Init default values
                guardrails_output = raw_response
                guard_leak_status = 0
                guardrails_time = 0.0

                lakera_output = raw_response
                lakera_leak_status = 0
                lakera_time = 0.0

                # Guardrails AI
                if use_guardrails:
                    guardrails_start = time.time()
                    guardrails_output, pii_detected = guardrails_ai_check(raw_response)
                    guardrails_end = time.time()
                    guardrails_time = round(guardrails_end - guardrails_start, 3)

                    guard_leaked_words = [word for word in detected_words if word in guardrails_output.lower()]
                    guard_leak_status = 1 if pii_detected and guard_leaked_words else 0

                # Lakera
                if use_lakera:
                    lakera_start = time.time()
                    lakera_result, lakera_data = lakera_pii_check(raw_response)
                    lakera_output = "Blocked by Lakera" if lakera_result == "blocked" else raw_response
                    lakera_leak_status = 1 if lakera_result == "blocked" else 0
                    lakera_end = time.time()
                    lakera_time = round(lakera_end - lakera_start, 3)

                # Base result for all cases
                base_columns = [
                    "Model", "User Prompt", "Raw Response",
                    "Raw Leak (Manual Check)", "Raw Response Time (seconds)"
                ]

                guardrails_columns = [
                    "Guardrails Output", "Guardrails Leak (Manual Check)", "Guardrails Time (seconds)"
                ]

                lakera_columns = [
                    "Lakera Output", "Lakera Leak (Manual Check)", "Lakera Time (seconds)"
                ]
                
                display_columns = base_columns.copy()
                if use_guardrails:
                    display_columns += guardrails_columns
                if use_lakera:
                    display_columns += lakera_columns

            result = {
                "Model": selected_model,
                "User Prompt": user_prompt,
                "Raw Response": raw_response,
                "Raw Leak (Manual Check)": raw_leak_status,
                "Raw Response Time (seconds)": response_time,
            }

            if use_guardrails:
                result.update({
                    "Guardrails Output": guardrails_output,
                    "Guardrails Leak (Manual Check)": guard_leak_status,
                    "Guardrails Time (seconds)": guardrails_time,
                })

            if use_lakera:
                result.update({
                    "Lakera Output": lakera_output,
                    "Lakera Leak (Manual Check)": lakera_leak_status,
                    "Lakera Time (seconds)": lakera_time,
                })

            results.append(result)
        
        # Convert to DataFrame
        results_df = pd.DataFrame(results)

        if not results_df.empty:
            st.write("### Test Results")

            # Define columns dynamically
            base_columns = [
                "Model", "User Prompt", "Raw Response",
                "Raw Leak (Manual Check)", "Raw Response Time (seconds)"
            ]
            guardrails_columns = [
                "Guardrails Output", "Guardrails Leak (Manual Check)", "Guardrails Time (seconds)"
            ]
            
            display_columns = base_columns + guardrails_columns if use_guardrails else base_columns
            st.dataframe(results_df[display_columns])

            # Save filtered results
            results_filename = f"{selected_csv.replace('.csv', '')}-{selected_model.replace('/','-')}-results.csv"
            results_filepath = os.path.join(TEST_SCRIPTS_DIR, results_filename)
            results_df[display_columns].to_csv(results_filepath, index=False)

            st.success(f"Results saved to: {results_filename}")
            st.download_button(
                label="Download Results CSV",
                data=results_df[display_columns].to_csv(index=False).encode("utf-8"),
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

    # Guardrail Selection
    use_guardrails = st.checkbox("GuardrailsAI - PII Detection", value=True)
    use_lakera = st.checkbox("Lakera Guard - Data Leakage", value=True)

    # Start Testing Button
    if st.button("Start Testing"):
        if selected_csv:
            tester.process_csv(selected_csv, selected_model, use_guardrails, use_lakera)
        else:
            st.error("Please select a CSV file for testing.")
    

# Run the Streamlit App
if __name__ == "__main__":
    main()

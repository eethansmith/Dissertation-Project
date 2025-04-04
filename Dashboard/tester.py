# tester.py

import os
import time
import pandas as pd
import streamlit as st
from openai import OpenAI

from constants import TEST_SCRIPTS_DIR
from guards import guardrails_ai_check, lakera_pii_check
from utils import format_result_filename, check_manual_leak, validate_csv_columns

# Guardrails AI Init
from guardrails.hub import DetectPII
from guardrails import Guard


class GuardrailsTester:
    """Class to handle guardrail testing for Large Language Models."""

    def __init__(self):
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
            uploaded_path = os.path.join(TEST_SCRIPTS_DIR, uploaded_file.name)
            with open(uploaded_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            self.csv_files.append(uploaded_file.name)
            st.success(f"Uploaded {uploaded_file.name}")

    def query_openrouter(self, model, system_prompt, user_prompt):
        """Query OpenRouter LLM API and return response + timing."""
        start = time.time()
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

        elapsed = round(time.time() - start, 3)
        return response, elapsed

    def process_csv(self, selected_csv, selected_model, use_guardrails=True, use_lakera=False):
        """Process CSV prompts, query LLM, and apply guardrails."""
        csv_path = os.path.join(TEST_SCRIPTS_DIR, selected_csv)
        df = pd.read_csv(csv_path)

        required_columns = {"System Prompt", "User Prompt", "Detected"}
        if not validate_csv_columns(df, required_columns):

            st.error("CSV missing required columns: 'System Prompt', 'User Prompt', 'Detected'")
            return

        st.write("### Running Tests...")
        results = []

        pii_guard = Guard().use(
            DetectPII, ["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD"], "fix"
        )

        for _, row in df.iterrows():
            system_prompt = str(row["System Prompt"])
            user_prompt = str(row["User Prompt"])
            detected_words = [w.strip().lower() for w in str(row["Detected"]).split(",")]

            with st.spinner(f"Querying model for prompt: {user_prompt[:30]}..."):
                raw_response, response_time = self.query_openrouter(selected_model, system_prompt, user_prompt)

                # Manual leak check
                raw_leaked_words = check_manual_leak(detected_words, raw_response)
                raw_leak = 1 if raw_leaked_words else 0

                # Default outputs
                guard_output = raw_response
                guard_leak = 0
                guard_time = 0.0

                lakera_output = raw_response
                lakera_leak_status = 0
                lakera_time = 0.0

                # Guardrails AI
                if use_guardrails:
                    guard_start = time.time()
                    guard_output, pii_detected = guardrails_ai_check(raw_response)
                    guard_time = round(time.time() - guard_start, 3)
                    guard_leaked = [w for w in detected_words if w in guard_output.lower()]
                    guard_leak = 1 if pii_detected and guard_leaked else 0

                # Lakera
                if use_lakera:
                    lakera_start = time.time()
                    lakera_result, _ = lakera_pii_check(raw_response)
                    lakera_output, lakera_leak_status = lakera_pii_check(raw_response)
                    lakera_time = round(time.time() - lakera_start, 3)
                    lakera_leaked = [w for w in detected_words if w in guard_output.lower()]
                    lakera_leak = 1 if pii_detected and guard_leaked else 0

                result = {
                    "Model": selected_model,
                    "User Prompt": user_prompt,
                    "Raw Response": raw_response,
                    "Raw Leak (Manual Check)": raw_leak,
                    "Raw Response Time (seconds)": response_time,
                }

                if use_guardrails:
                    result.update({
                        "Guardrails Output": guard_output,
                        "Guardrails Leak (Manual Check)": guard_leak,
                        "Guardrails Time (seconds)": guard_time,
                    })

                if use_lakera:
                    result.update({
                        "Lakera Output": lakera_output,
                        "Lakera Leak (Manual Check)": lakera_leak,
                        "Lakera Time (seconds)": lakera_time,
                    })

                results.append(result)
 
        results_df = pd.DataFrame(results)
        if results_df.empty:
            st.success("No PII detected in model outputs!")
            return

        # Display and export results
        st.write("### Test Results")

        base_cols = [
            "Model", "User Prompt", "Raw Response",
            "Raw Leak (Manual Check)", "Raw Response Time (seconds)"
        ]
        if use_guardrails:
            base_cols += [
                "Guardrails Output", "Guardrails Leak (Manual Check)", "Guardrails Time (seconds)"
            ]
        if use_lakera:
            base_cols += [
                "Lakera Output", "Lakera Leak (Manual Check)", "Lakera Time (seconds)"
            ]

        st.dataframe(results_df[base_cols])

        filename = format_result_filename(selected_csv, selected_model)
        filepath = os.path.join(TEST_SCRIPTS_DIR, filename)
        results_df[base_cols].to_csv(filepath, index=False)

        st.success(f"Results saved to: {filename}")
        st.download_button(
            label="Download Results CSV",
            data=results_df[base_cols].to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
        )

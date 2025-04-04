import streamlit as st
from tester import GuardrailsTester
from constants import MODEL_OPTIONS


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
    
    # Run Guardrails on raw LLM output or PII Aware LLM Output
    warn_llm_pii = st.checkbox("Include PII Prevention in LLM Prompt")
    # Addition: more info to tailor the prompt addition
    
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

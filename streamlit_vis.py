import streamlit as st

st.title("PII Guardrail Efficacy Testing Results")

st.write("The following results are recorded when testing a set script given to the system prompt that includes lots of synthetic PII data.")
st.write("The system prompt is tested in four different conditions: Original, Modified Before, Modified After, and Modified Detailed.")
st.write("The system prompt is tested 5 times in each condition to evaluate the guardrail efficacy.")

st.image("")
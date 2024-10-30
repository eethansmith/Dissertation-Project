import streamlit as st
from GPT_API_CALL import pii_extraction
from pii_detection import pii_detection
from append_to_csv import append_data

st.title("Personal Identifiable Information (PII) Detection and Extraction")

user_input = st.text_area("Enter some text:")

if user_input:
    st.write(f"User input: {user_input}")
    # Score the chances of the text containing PII
    name_detection, email_detection, number_detection, bank_details_detection, company_details_detection = pii_detection(user_input)
    st.write(f"{name_detection}% chance input includes name")
    st.write(f"{email_detection}% chance input includes email address")
    st.write(f"{number_detection}% chance input includes a phone number")
    st.write(f"{bank_details_detection}% chance input includes bank details")
    st.write(f"{company_details_detection}% chance input includes company details")

    pii_extracted = pii_extraction(user_input)
    st.write(f"PII extraction: {pii_extracted}")
    data = {
        "User Input": user_input,
        "Name Detected": name_detection,
        "Email Detected": email_detection,
        "Phone Number Detected": number_detection,
        "Bank Details Detected": bank_details_detection,
        "Company Detected": company_details_detection,
        "PII Extracted": pii_extracted}
    append_data(data)
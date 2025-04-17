import streamlit as st
from GPT_API_CALL import pii_extraction
from pii_detection import pii_detection
from append_to_csv import append_data

st.title("Personal Identifiable Information (PII) Detection and Extraction")

st.write("The following is a proof of concept demo of how AI can be used to assess the security/vulnerability of an input from a user. This can prevent data leak and data extraction as a model like this could be put in place to flag the inputs could contain sensitive information.")

st.write("We are looking for PII data this is Personal Identifiable Information, this is any data about a person that could allow connection to them, where this process is only looking for certain PII (Email, Phone Number, Bank Details, Company Details). This will go on to test if this system can be used to identify PII relating to injury data or experience data.")

st.write("#### The diagram below shows the process of how the system works:")
st.image("PII_detection_diagram.png", use_column_width=True)

user_input = st.text_area("Enter some text:")

if user_input:
    st.write("## User Input:")
    st.write(f"{user_input}")
    # Score the chances of the text containing PII
    st.write("## AI Assessement of PII Included:")
    name_detection, email_detection, number_detection, bank_details_detection, company_details_detection = pii_detection(user_input)
    st.write(f"{name_detection}% chance input includes name")
    st.write(f"{email_detection}% chance input includes email address")
    st.write(f"{number_detection}% chance input includes a phone number")
    st.write(f"{bank_details_detection}% chance input includes bank details")
    st.write(f"{company_details_detection}% chance input includes company details")

    pii_extracted = pii_extraction(user_input)
    st.write("## PII Lifted Response:")
    st.write(f"{pii_extracted}")
    data = {
        "User Input": user_input,
        "Name Detected": name_detection,
        "Email Detected": email_detection,
        "Phone Number Detected": number_detection,
        "Bank Details Detected": bank_details_detection,
        "Company Detected": company_details_detection,
        "PII Extracted": pii_extracted}
    append_data(data)
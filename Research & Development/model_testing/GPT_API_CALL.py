from openai import OpenAI
import streamlit as st

openai_api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=openai_api_key)

def get_answer(prompt, info):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{info}"}
        ],
        temperature=1.71,
        max_tokens=200,
    )
    return response.choices[0].message.content


def pii_extraction(user_input):
    prompt = f"""
    You are a Personal Identifiable Information (PII) extraction model. Please extract all the information that could be used to identify any person from the following text provided and return the text in as much detail as possible without any PII information.
    Personally Identifiable Information (PII) is any data that can be used to identify a person, either directly or indirectly. PII is considered sensitive data and is often used in identity theft. Examples of PII include:
Full name
Mailing address
Telephone number
Email address
Medical records
Financial information, such as credit card numbers, bank accounts, or credit report information
Passport information, such as places and dates of travel
Internet account numbers and passwords
Biometric information
Any description that could be used to identify a person (e.g. physical description, attributes, very specific location descriptions.) 
Non-sensitive and indirect PII includes the previously noted quasi-identifying information, which is often a matter of public record or so anonymously collected that it is not easily tied to an individual on its own.
Only respond with Personal Identifiable Information (PII) removed, do not explain the reasoning for the response.
    """

    info = f"""{user_input}"""

    scoring = get_answer(prompt, info)
    return scoring

#print(pii_extraction("Jet bobed and weaved through the trees, and safley landed on the other side of the river. Where Bob who had lost his finger in an engineering fault the day before, was waiting for the passengers to collect their luggage. for more details contact 123-456-7890 or email at amrpeet@gmal.com"))
#print(pii_extraction("the A380 fighter jet made a last minute bob ston, was left to weave and ducked through the trees, and landed on the other side of the river. - milk.eggs @mod.com"))
import re
from openai import OpenAI
from GPT_API_CALL import get_answer

def extract_number(text):
    # Use regex to find all numeric characters and join them into a single number string
    match = re.findall(r'\d+', text)
    return int(''.join(match)) if match else 0  # Return 0 if no number is found

def name_detection(user_input):
    prompt = (
        "You're a PII detection and prevention Large Language Model with the specific aim to detect the inclusion of a Name within the user's input. "
        "Provide an integer value that determines the probability the user input contains a name."
    )
    response = get_answer(prompt, f"The user's input is: '{user_input}' scoring the possibility of containing a name:")
    return extract_number(response)

def email_detection(user_input):
    prompt = (
        "You're a PII detection and prevention Large Language Model with the specific aim to detect the inclusion of an email address within the user's input. "
        "Provide an integer value that determines the probability the user input contains an email address."
    )
    response = get_answer(prompt, f"The user's input is: '{user_input}' scoring the possibility of containing an email address:")
    return extract_number(response)

def phone_number_detection(user_input):
    prompt = (
        "You're a PII detection and prevention Large Language Model with the specific aim to detect the inclusion of a phone number within the user's input. "
        "Provide an integer value that determines the probability the user input contains a phone number."
    )
    response = get_answer(prompt, f"The user's input is: '{user_input}' scoring the possibility of containing a phone number:")
    return extract_number(response)

def bank_details_detection(user_input):
    prompt = (
        "You're a PII detection and prevention Large Language Model with the specific aim to detect the inclusion of bank details within the user's input. "
        "Provide an integer value that determines the probability the user input contains bank details."
    )
    response = get_answer(prompt, f"The user's input is: '{user_input}' scoring the possibility of containing bank details:")
    return extract_number(response)

def company_details_detection(user_input):
    prompt = (
        "You're a PII detection and prevention Large Language Model with the specific aim to detect the inclusion of company details within the user's input. "
        "Provide an integer value that determines the probability the user input contains company details."
    )
    response = get_answer(prompt, f"The user's input is: '{user_input}' scoring the possibility of containing company details:")
    return extract_number(response)

def pii_detection(user_input):
    return name_detection(user_input), email_detection(user_input), phone_number_detection(user_input), bank_details_detection(user_input), company_details_detection(user_input)
import requests
import streamlit as st

def lakera_pii_check(text):
    """
    Uses Lakera Guard API to determine if text contains PII.
    If PII is detected (blocked), returns redacted response.

    Args:
        text (str): LLM-generated output.

    Returns:
        (str): Either "Redacted by Lakera Guard" or original text
        (bool): True if PII was detected (blocked), False if allowed
    """
    api_key = st.secrets["LAKERA_API_KEY"]
    url = "https://api.lakera.ai/v2/guard"  # Update this URL based on Lakera's latest API endpoint

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": text
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        status = result.get("result", "error")

        if status == "blocked":
            return "Redacted by Lakera Guard", True
        elif status == "allowed":
            return text, False
        else:
            return f"Lakera returned unknown result: {status}", True

    except requests.exceptions.RequestException as e:
        return f"Lakera Error: {str(e)}", True

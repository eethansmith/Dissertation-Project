import requests
import streamlit as st

# Setup persistent session for better performance
session = requests.Session()

def lakera_pii_check(text):
    """
    Calls the Lakera Guard API to check if text contains PII.
    
    Args:
        text (str): The generated text to inspect.

    Returns:
        Tuple[str, bool]: Redacted or original output, and PII detection status.
    """
    api_key = st.secrets["LAKERA_API_KEY"]
    url = "https://api.lakera.ai/v2/guard"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": text
    }

    try:
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Handle the response
        result = data.get("result")
        redacted_text = data.get("redacted_prompt", "Redacted by Lakera Guard")

        if result == "blocked":
            return redacted_text, True
        elif result == "allowed":
            return text, False
        else:
            return f"[Lakera Warning] Unknown result: {result}", True

    except requests.exceptions.RequestException as e:
        return f"[Lakera Error] {str(e)}", True

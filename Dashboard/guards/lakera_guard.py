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
    
    ## Guard input must be in JSON format as follows:
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are preventing the extraction of PII from the provided text."
            },
            {
                "role": "assistant",
                "content": text
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Handle the response
        result = data.get("result")
        redacted_text = data.get("redacted_prompt", "Redacted by Lakera Guard")

        if result == "blocked":
            return redacted_text
        elif result == "allowed":
            return text
        else:
            return f"[Lakera Warning] Unknown result: {result}"

    except requests.exceptions.RequestException as e:
        return f"[Lakera Error] {str(e)}"

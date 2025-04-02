#imports for lakera requests
import requests
import streamlit as st

def lakera_pii_check(text):
    """
    Uses Lakera API to check for PII in model output.

    Args:
        text (str): LLM-generated output.

    Returns:
        (str): "blocked", "allowed", or "error"
        (dict): Full API response or error message
    """
    api_key = st.secrets["LAKERA_API_KEY"]
    url = "https://api.lakera.ai/guardrails/check"

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
        return result.get("result", "error"), result
    except Exception as e:
        return "error", {"error": str(e)}

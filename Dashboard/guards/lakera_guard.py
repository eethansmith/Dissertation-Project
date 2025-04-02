# Lakera_Guard
import requests
import streamlit as st

def lakera_pii_check(text):
    api_key = st.secrets["LAKERA_API_KEY"]  # Must be in .streamlit/secrets.toml
    url = "https://api.lakera.ai/guardrails/check"  # Confirm with latest docs if needed

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
        return result["result"], result  # e.g., "blocked", "allowed", etc.
    except Exception as e:
        return "error", {"error": str(e)}

# Lakera_Guard.py

from lakera import Lakera
import streamlit as st

def lakera_pii_check(text):
    lakera_client = Lakera(api_key=st.secrets["LAKERA_API_KEY"])
    try:
        response = lakera_client.guardrails.check(prompt=text)
        result = response.dict()
        return result["result"], result  # e.g., "blocked" or "allowed"
    except Exception as e:
        return "error", {"error": str(e)}

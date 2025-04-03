import requests
import streamlit as st

session = requests.Session()

def lakera_pii_check(text, project_id=None, session_id=None, user_id=None):
    """
    Calls the Lakera Guard v2 API with a messages-based structure.
    Detects whether the assistant output contains PII or policy violations.
    
    Args:
        text (str): LLM-generated assistant response to check.
        project_id (str): Optional Lakera project ID.
        session_id (str): Optional session tracking.
        user_id (str): Optional user tracking.

    Returns:
        Tuple[str, bool, dict]: (Possibly redacted) text, PII flag, breakdown metadata.
    """
    api_key = st.secrets["LAKERA_API_KEY"]
    url = "https://api.lakera.ai/v2/guard"

    # Format messages for Lakera
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
        ],
        "payload": True,
    }

    # Optionally add project + tracking metadata
    if project_id:
        payload["project_id"] = project_id
    if session_id or user_id:
        payload["metadata"] = {}
        if session_id:
            payload["metadata"]["session_id"] = session_id
        if user_id:
            payload["metadata"]["user_id"] = user_id

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = session.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        flagged = data.get("flagged", False)
        detected_chunks = data.get("payload", [])

        # Optional: redact detected chunks manually
        redacted_text = text
        if flagged and detected_chunks:
            for chunk in sorted(detected_chunks, key=lambda x: x["start"], reverse=True):
                redacted_text = (
                    redacted_text[:chunk["start"]] +
                    "[REDACTED]" +
                    redacted_text[chunk["end"]:]
                )

        return redacted_text if flagged else text, flagged

    except requests.exceptions.RequestException as e:
        return f"[Lakera Error] {str(e)}", True

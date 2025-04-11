import os
import requests
from dotenv import load_dotenv
load_dotenv()

session = requests.Session()

def lakera_pii_check(text, project_id=None, session_id=None, user_id=None):
    """
    Calls the Lakera Guard v2 API with a messages-based structure.
    Detects whether the assistant output contains PII or policy violations.
    """
    api_key = os.getenv("LAKERA_API_KEY")
    if not api_key:
        return "[Lakera Error] LAKERA_API_KEY not found in environment variables"

    url = "https://api.lakera.ai/v2/guard"

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

        redacted_text = text
        if flagged and detected_chunks:
            for chunk in sorted(detected_chunks, key=lambda x: x["start"], reverse=True):
                redacted_text = (
                    redacted_text[:chunk["start"]] +
                    "[REDACTED]" +
                    redacted_text[chunk["end"]:]
                )

        return redacted_text if flagged else text

    except requests.exceptions.RequestException as e:
        return f"[Lakera Error] {str(e)}"

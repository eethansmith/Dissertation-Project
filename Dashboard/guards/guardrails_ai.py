# GuardrailsAI_Guard.py

from guardrails.hub import DetectPII

def guardrails_ai_check(text, pii_types=None):
    try:
        # Initialize the Guardrails PII detector
        pii_validator = DetectPII()

        # Validate the text (this flags if PII is present)
        validated_response, error = pii_validator.validate(text)

        # If PII is found, redact it using tags like <PERSON>
        if error:
            redacted_text = pii_validator.redact(text)
            return redacted_text
        else:
            return text

    except Exception as e:
        return f"[SUPPRESSED: ERROR] Guardrails failed to process text - {str(e)}"

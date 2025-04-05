# GuardrailsAI_Guard.py
from guardrails import Guard
from guardrails.hub import DetectPII

def guardrails_ai_check(text, pii_types=None, mode="fix"):
    """
    Validates the input text using Guardrails AI's DetectPII tool.

    Args:
        text (str): The LLM response to check.
        pii_types (list): List of PII types to detect.
        mode (str): The handling mode ("fix", "filter", etc.).

    Returns:
        (str): Validated output.
        (bool): Whether PII was detected and fixed.
    """
    if pii_types is None:
        pii_types = ["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON", "CREDIT_CARD"]
    try:
        pii_guard = Guard().use(DetectPII, pii_types=pii_types, mode=mode)
        result = pii_guard.validate(text)

        validated_output = result.validated_output
        if validated_output:
            return validated_output, True
        else:
            return "[REDACTED]: PII detected but could not be fixed", False
    except Exception:
        return "[SUPPRESSED]: This response likely includes PII", False

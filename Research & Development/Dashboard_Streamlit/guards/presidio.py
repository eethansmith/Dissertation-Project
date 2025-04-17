from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def presidio_pii_check(text, project_id=None, session_id=None, user_id=None):
    """
    Uses Microsoft Presidio to detect and optionally redact PII in a string.
    
    Args:
        text (str): The text to check for PII.
        project_id (str): Optional project tracking.
        session_id (str): Optional session tracking.
        user_id (str): Optional user tracking.

    Returns:
        Tuple[str, bool, list]: (Possibly redacted) text, PII flag, breakdown metadata.
    """
    try:
        # Analyze text
        results = analyzer.analyze(text=text, language='en')

        flagged = len(results) > 0
        redacted_text = text
        breakdown = []

        if flagged:
            redacted_result = anonymizer.anonymize(text=text, analyzer_results=results)
            redacted_text = redacted_result.text
            breakdown = [
                {
                    "type": r.entity_type,
                    "score": r.score,
                    "start": r.start,
                    "end": r.end,
                    "text": text[r.start:r.end]
                }
                for r in results
            ]

        return redacted_text

    except Exception as e:
        return f"[Presidio Error] {str(e)}"

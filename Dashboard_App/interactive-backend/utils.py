import os

def format_result_filename(csv_name: str, model_name: str) -> str:
    """Format result CSV filename based on CSV and model name."""
    base_name = csv_name.replace('.csv', '')
    model_clean = model_name.replace('/', '-')
    return f"{base_name}-{model_clean}-results.csv"


def check_manual_leak(detected_words, text):
    """Check if any of the detected words appear in the text (case insensitive)."""
    text_lower = text.lower()
    return [word for word in detected_words if word in text_lower]


def validate_csv_columns(df, required_cols):
    """Check that all required columns are in the DataFrame."""
    return required_cols.issubset(set(df.columns))

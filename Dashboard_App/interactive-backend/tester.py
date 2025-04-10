import os
import time
import pandas as pd
from openai import OpenAI
from guards import lakera_pii_check, presidio_pii_check
from utils import check_manual_leak, validate_csv_columns

from dotenv import load_dotenv
load_dotenv()

TEST_SCRIPTS_DIR = "test-scripts"
os.makedirs(TEST_SCRIPTS_DIR, exist_ok=True)

def run_tests_headless(selected_csv, selected_model, prompt_addition, use_guardrails=False, use_lakera=False, use_presidio=False):
    """
    Processes a test CSV file and runs tests in a headless manner.
    
    Parameters:
      - selected_csv (str): the CSV file name (with extension) located in TEST_SCRIPTS_DIR.
      - selected_model (str): the language model to query.
      - prompt_addition (str): text to prepend to each system prompt (e.g., the piiPrompt).
      - use_guardrails (bool): whether to apply the guardrails_ai_check.
      - use_lakera (bool): whether to apply the lakera_pii_check.
      - use_presidio (bool): whether to apply the presidio_pii_check.
    
    Returns:
      dict: containing keys "results" (a list of result dicts) and "total_time" (the sum of response times).
    """
    csv_path = os.path.join(TEST_SCRIPTS_DIR, selected_csv)
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return {"error": f"Error reading CSV '{selected_csv}': {e}"}

    required_columns = {"System Prompt", "User Prompt", "Detected"}
    if not validate_csv_columns(df, required_columns):
        return {"error": "CSV missing required columns: 'System Prompt', 'User Prompt', 'Detected'"}

    # Set up your OpenRouter client. Here we read the API key from an environment variable.
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        return {"error": "Missing OPENROUTER_API_KEY environment variable"}
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key
    )

    results = []
    total_time = 0.0

    for _, row in df.iterrows():
        system_prompt = prompt_addition + str(row["System Prompt"])
        user_prompt = str(row["User Prompt"])
        detected_words = [w.strip().lower() for w in str(row["Detected"]).split(",")]

        # Query the model.
        start = time.time()
        try:
            completion = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            raw_response = completion.choices[0].message.content
        except Exception as e:
            raw_response = f"API Error: {e}"
        response_time = round(time.time() - start, 3)
        total_time += response_time

        raw_leak = 1 if check_manual_leak(detected_words, raw_response) else 0

        # Initialize guard outputs to default (raw_response).
        guard_output = raw_response
        guard_leak = 0
        guard_time = 0.0

        lakera_output = raw_response
        lakera_leak = 0
        lakera_time = 0.0

        presidio_output = raw_response
        presidio_leak = 0
        presidio_time = 0.0

        #if use_guardrails:
        #    start_guard = time.time()
        #    guard_output = guardrails_ai_check(raw_response)
        #    guard_time = round(time.time() - start_guard, 3)
        #    guard_leak = 1 if any(word in guard_output.lower() for word in detected_words) else 0

        if use_lakera:
            start_lakera = time.time()
            lakera_output = lakera_pii_check(raw_response)
            lakera_time = round(time.time() - start_lakera, 3)
            lakera_leak = 1 if any(word in lakera_output.lower() for word in detected_words) else 0

        if use_presidio:
            start_presidio = time.time()
            presidio_output = presidio_pii_check(raw_response)
            presidio_time = round(time.time() - start_presidio, 3)
            presidio_leak = 1 if any(word in presidio_output.lower() for word in detected_words) else 0

        result = {
            "Model": selected_model,
            "User Prompt": user_prompt,
            "Raw Response": raw_response,
            "Raw Leak (Manual Check)": raw_leak,
            "Raw Response Time (seconds)": response_time,
        }
        #if use_guardrails:
        #    result.update({
        #        "Guardrails Output": guard_output,
        #        "Guardrails Leak (Manual Check)": guard_leak,
        #        "Guardrails Time (seconds)": guard_time,
        #    })
        
        if use_lakera:
            result.update({
                "Lakera Output": lakera_output,
                "Lakera Leak (Manual Check)": lakera_leak,
                "Lakera Time (seconds)": lakera_time,
            })
        if use_presidio:
            result.update({
                "Presidio Output": presidio_output,
                "Presidio Leak (Manual Check)": presidio_leak,
                "Presidio Time (seconds)": presidio_time,
            })

        results.append(result)

    return {"results": results, "total_time": total_time}

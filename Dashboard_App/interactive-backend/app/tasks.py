# app/tasks.py

import os
import pandas as pd
from datetime import datetime
from threading import Thread
from tester import run_tests_headless
from .utils import update_test_record
from .config import TEST_RESULTS_DIR

def background_test_runner(test_id, test_script, model, prompt_addition, guard_options, csv_filename):
    """Runs tests in a background thread."""
    test_results = run_tests_headless(
        selected_csv=test_script,
        selected_model=model,
        prompt_addition=prompt_addition,
        use_guardrails=guard_options.get('guardrailsAI', False),
        use_lakera=guard_options.get('lakeraGuard', False),
        use_presidio=guard_options.get('presidio', False)
    )

    if "error" in test_results:
        print(f"Test failed: {test_results['error']}")
        return

    results_df = pd.DataFrame(test_results["results"])
    results_filename = os.path.join(TEST_RESULTS_DIR, f"{test_id}.csv")

    try:
        results_df.to_csv(results_filename, index=False)
    except Exception as e:
        print(f"Error saving results CSV: {e}")

    total_time = int(test_results.get("total_time", 0))
    update_test_record(csv_filename, test_id, total_time, False)

def run_in_background(*args, **kwargs):
    """Helper to execute the background task in a new thread."""
    thread = Thread(target=background_test_runner, args=args, kwargs=kwargs)
    thread.start()

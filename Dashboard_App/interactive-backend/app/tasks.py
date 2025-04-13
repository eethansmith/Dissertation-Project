# app/tasks.py

import os
import pandas as pd
from datetime import datetime
from threading import Thread
from tester import run_tests_headless
from .utils import update_test_record
from .config import TEST_RESULTS_DIR

def process_test_data(test_id):
    """
    Process test data by loading the results CSV, calculating average and total times
    for both raw response and the individual guardrail times (if applied),
    then saving a summary CSV in:
        TEST_RESULTS_DIR/<test_id>/pie_chart.csv
    """
    # Define folder structure: TEST_RESULTS_DIR/test_id/
    test_folder = os.path.join(TEST_RESULTS_DIR, str(test_id))
    os.makedirs(test_folder, exist_ok=True)

    results_filename = os.path.join(TEST_RESULTS_DIR, f"{test_id}.csv")

    try:
        df = pd.read_csv(results_filename)
    except Exception as e:
        print(f"Error loading results CSV for processing: {e}")
        return

    summary_data = {}

    # Process Raw Response Time
    if "Raw Response Time (seconds)" in df.columns:
        avg_raw = df["Raw Response Time (seconds)"].mean()
        total_raw = df["Raw Response Time (seconds)"].sum()
        summary_data["Average Raw Response Time (seconds)"] = [avg_raw]
        summary_data["Total Raw Response Time (seconds)"] = [total_raw]
    else:
        print("Column 'Raw Response Time (seconds)' not found in results.")
        return

    overall_total = total_raw  # Start with raw total

    # Define potential guardrail timing columns and their labels
    guardrail_columns = {
        "Guardrails Time (seconds)": "Guardrails",
        "Lakera Time (seconds)": "Lakera",
        "Presidio Time (seconds)": "Presidio"
    }

    for col, label in guardrail_columns.items():
        if col in df.columns:
            avg_time = df[col].mean()
            total_time = df[col].sum()
            summary_data[f"Average {label} Time (seconds)"] = [avg_time]
            summary_data[f"Total {label} Time (seconds)"] = [total_time]
            overall_total += total_time

    summary_data["Overall Total Time (seconds)"] = [overall_total]

    summary_df = pd.DataFrame(summary_data)

    summary_df = summary_df.round(3)

    summary_filename = os.path.join(test_folder, "pie_chart.csv")

    try:
        summary_df.to_csv(summary_filename, index=False)
        print(f"Data processing complete. Summary CSV saved to: {summary_filename}")
    except Exception as e:
        print(f"Error saving summary CSV: {e}")
        
        
        # Create a summary for manual checks (success metrics)
    success_data = {}
    
    # Total raw produced tests = number of rows
    total_tests = len(df)
    success_data["Total Raw Produced"] = [total_tests]
    
    # Total raw manual checks (sum of 0's and 1's: 1's count as failures)
    if "Manual Checks" in df.columns:
        total_manual_raw = df["Manual Checks"].sum()
    else:
        total_manual_raw = 0
    success_data["Total Raw Manual Checks"] = [total_manual_raw]
    
    # For each guardrail timing column (if the guardrail was applied, indicated by its existence)
    guardrail_columns = {
        "Guardrails Time (seconds)": "Guardrails",
        "Lakera Time (seconds)": "Lakera",
        "Presidio Time (seconds)": "Presidio"
    }
    
    for col, label in guardrail_columns.items():
        if col in df.columns:
            # Count tests where this guardrail was applied (i.e. non-null entries)
            guardrail_count = df[col].notna().sum()
            # Sum the manual checks for those tests (if Manual Checks exists)
            guardrail_manual = df.loc[df[col].notna(), "Manual Checks"].sum() if "Manual Checks" in df.columns else 0
            success_data[f"Total {label} Produced"] = [guardrail_count]
            success_data[f"Total {label} Manual Checks"] = [guardrail_manual]
    
    # Create the DataFrame and save as "sucess_bar_chart.csv" in the test folder.
    success_df = pd.DataFrame(success_data)
    success_filename = os.path.join(test_folder, "sucess_bar_chart.csv")
    
    try:
        success_df.to_csv(success_filename, index=False)
        print(f"Success data processing complete. CSV saved to: {success_filename}")
    except Exception as e:
        print(f"Error saving success CSV: {e}")


def background_test_runner(test_id, test_script, model, prompt_addition, guard_options, csv_filename):
    """Runs tests in a background thread and then processes the resulting CSV."""
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

    # Save the raw test results
    results_df = pd.DataFrame(test_results["results"])
    results_filename = os.path.join(TEST_RESULTS_DIR, f"{test_id}.csv")

    try:
        results_df.to_csv(results_filename, index=False)
    except Exception as e:
        print(f"Error saving results CSV: {e}")

    total_time = int(test_results.get("total_time", 0))
    update_test_record(csv_filename, test_id, total_time, False)

    # Process the data after test execution
    process_test_data(test_id)

def run_in_background(*args, **kwargs):
    """Helper to execute the background task in a new thread."""
    thread = Thread(target=background_test_runner, args=args, kwargs=kwargs)
    thread.start()

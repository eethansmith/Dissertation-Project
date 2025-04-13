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
        
        
            # --- New Code: Generate sucess_bar_chart.csv ---
    success_rows = []

    # Only include columns that end with '(Manual Check)'
    manual_check_cols = [col for col in df.columns if col.endswith("(Manual Check)")]

    for col in manual_check_cols:
        # Get stage name from column (e.g., 'Raw Leak (Manual Check)' → 'Raw')
        stage = col.split(" ")[0]
        passed = (df[col] == 0).sum()
        failed = (df[col] == 1).sum()
        success_rows.append({
            "Stage": stage,
            "Passed": passed,
            "Failed": failed
        })

    # Create DataFrame and save
    success_df = pd.DataFrame(success_rows)
    success_filename = os.path.join(test_folder, "sucess_bar_chart.csv")

    try:
        success_df.to_csv(success_filename, index=False)
        print(f"Success bar chart CSV saved to: {success_filename}")
    except Exception as e:
        print(f"Error saving success CSV: {e}")
        
    question_data = {}

    # Create Test Number based on the row index (starting from 1)
    question_data["Test Number"] = df.index + 1

    # Get the User Prompt column, if it exists.
    if "User Prompt" in df.columns:
        question_data["User Prompt"] = df["User Prompt"]
    else:
        question_data["User Prompt"] = [""] * len(df)

    # Find all columns that end with "(Manual Check)"
    manual_check_cols = [col for col in df.columns if col.endswith("(Manual Check)")]

    # For each found manual check column, extract the stage name and copy the column data.
    for col in manual_check_cols:
        # Example: "Raw Leak (Manual Check)" → stage = "Raw"
        stage = col.split(" ")[0]
        question_data[stage] = df[col]

    # Create DataFrame for the question line graph
    question_df = pd.DataFrame(question_data)

    # Optionally, force the column order with "Test Number" and "User Prompt" first.
    # The remaining columns are added in the order they appear.
    columns_order = ["Test Number", "User Prompt"] + [col for col in question_df.columns if col not in ("Test Number", "User Prompt")]
    question_df = question_df[columns_order]

    # Save the new CSV to the same test folder with the name "question_line_graph.csv"
    question_filename = os.path.join(test_folder, "question_line_graph.csv")

    try:
        question_df.to_csv(question_filename, index=False)
        print(f"Question line graph CSV saved to: {question_filename}")
    except Exception as e:
        print(f"Error saving question line graph CSV: {e}")
        
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

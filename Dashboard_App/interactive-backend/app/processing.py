import os
import pandas as pd

def process_chart1_data(results_csv_path, test_id):
    """
    Reads raw test results from a CSV, aggregates time for different components,
    and writes the summary to a chart1 CSV file in the testID folder.
    """
    # Load the raw results (update this with your actual CSV structure)
    df = pd.read_csv(results_csv_path)
    
    # Example aggregation: summing the times (adjust as per your requirements)
    # (Assuming the CSV has the following columns; otherwise adjust accordingly.)
    aggregated_times = {
        "Raw Output": df["raw_time"].sum(),
        "Guardrails AI": df["guardrailsAI_time"].sum(),
        "Lakera Guard": df["lakeraGuard_time"].sum(),
        "Presidio": df["presidio_time"].sum(),
    }
    
    # Prepare a list of dictionary items for DataFrame conversion.
    data_rows = [{"category": category, "time": time_value} 
                 for category, time_value in aggregated_times.items()]
    
    # Create a DataFrame and save to CSV
    chart1_df = pd.DataFrame(data_rows)
    test_folder = os.path.join(TEST_RESULTS_DIR, test_id)
    os.makedirs(test_folder, exist_ok=True)
    chart1_filename = os.path.join(test_folder, "chart1.csv")
    try:
        chart1_df.to_csv(chart1_filename, index=False)
        print(f"Chart1 data saved to {chart1_filename}")
    except Exception as e:
        print(f"Error saving Chart1 data: {e}")

import csv
import os

# Define the CSV file path
csv_file = "user_input.csv"

def append_data(data):
    # Define the column headers
    headers = ["User Input", "Name Detected", "Email Detected", "Phone Number Detected", "Bank Details Detected", "Company Detected", "PII Extracted"]

    # Check if the CSV file exists
    file_exists = os.path.isfile(csv_file)

    # Open the CSV file in append mode
    with open(csv_file, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        # If the file doesn't exist, write the header first
        if not file_exists:
            writer.writeheader()

        # Append the data as a new row
        writer.writerow(data)
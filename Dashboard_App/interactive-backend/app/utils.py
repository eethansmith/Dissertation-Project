# app/utils.py

import csv

def update_test_record(csv_filename, test_id, time_taken, in_progress):
    """Update the test record in test_list.csv with the total time taken and status."""
    try:
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

        for row in rows:
            try:
                if int(row.get('testID', -1)) == int(test_id):
                    row['timeTaken'] = str(time_taken)
                    row['inProgress'] = 'True' if in_progress else 'False'
            except ValueError:
                continue  # Skip bad rows

        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['testID', 'model', 'testSet', 'guardrails', 'timeTaken', 'date', 'piiPrompt', 'inProgress']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    except Exception as e:
        print(f"Error updating test record: {e}")

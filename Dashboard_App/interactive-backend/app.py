import os
import time
import csv
import pandas as pd
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import the headless test-run function from tester.py.
from tester import run_tests_headless

app = Flask(__name__)
CORS(app)

# Set the upload folder (must match the TEST_SCRIPTS_DIR in tester.py).
UPLOAD_FOLDER = 'test-scripts'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

TEST_RESULTS_DIR = 'test-dataset'
os.makedirs(TEST_RESULTS_DIR, exist_ok=True)

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

# Endpoint to list tests.
@app.route('/api/tests')
def get_tests():
    data = []
    csv_filename = 'test_list.csv'
    try:
        with open(csv_filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    if not row or None in row:
                        print("Skipping malformed row:", row)
                        continue
                    row['testID'] = int(row.get('testID', 0))
                    row['timeTaken'] = int(row.get('timeTaken', 0))
                    guardrails_raw = row.get('guardrails', '')
                    row['guardrails'] = guardrails_raw.split(',') if guardrails_raw else []
                    in_progress_value = row.get('inProgress')
                    if in_progress_value == 'True':
                        row['inProgress'] = True
                    elif in_progress_value == 'False':
                        row['inProgress'] = False
                    else:
                        row['inProgress'] = None
                    row['piiPrompt'] = row.get('piiPrompt', '')
                    data.append(row)
                except Exception as e:
                    print(f"Skipping row due to error: {e}\nRow: {row}")
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(data)

# Endpoint to list available test script names.
@app.route('/api/test-scripts')
def get_test_scripts():
    script_folder = app.config['UPLOAD_FOLDER']
    try:
        files = [f for f in os.listdir(script_folder) if f.endswith('.csv')]
        script_names = [os.path.splitext(f)[0] for f in files]
        return jsonify(script_names)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint for uploading a new test script.
@app.route('/api/upload-test-script', methods=['POST'])
def upload_test_script():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(save_path)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to start a test.
@app.route('/api/start-test', methods=['POST'])
def start_test():
    data = request.get_json()

    # Extract fields from the payload.
    model = data.get('model')
    # Assuming the front-end sends the script name without the .csv extension.
    test_script = data.get('testScript') + ".csv"
    pii_prompt = data.get('piiPrompt', '')
    guardrails = data.get('guardrails', {})

    # Use the pii_prompt as an addition to system prompts if desired.
    prompt_addition = pii_prompt if pii_prompt else ""

    # Build the guardrail options dictionary.
    guard_options = {
        "guardrailsAI": guardrails.get('guardrailsAI', False),
        "lakeraGuard": guardrails.get('lakeraGuard', False),
        "presidio": guardrails.get('presidio', False)
    }
    # Create a displayable list for the record.
    guard_list = []
    if guard_options["guardrailsAI"]:
        guard_list.append("GuardrailsAI - PII Detection")
    if guard_options["lakeraGuard"]:
        guard_list.append("Lakera Guard - Data Leakage")
    if guard_options["presidio"]:
        guard_list.append("Presidio - PII Detection")

    now = datetime.now()
    date_only_str = now.strftime("%Y-%m-%d")

    # Generate a unique testID.
    test_id = 1
    csv_filename = 'test_list.csv'
    try:
        if os.path.exists(csv_filename):
            with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                test_ids = [int(row['testID']) for row in reader if row.get('testID')]
                if test_ids:
                    test_id = max(test_ids) + 1
    except Exception as e:
        test_id = 1

    new_test = {
        'testID': test_id,
        'model': model,
        'testSet': test_script,
        'guardrails': ','.join(guard_list),
        'timeTaken': 0,  # Will update after tests complete.
        'date': date_only_str,
        'piiPrompt': pii_prompt,
        'inProgress': True
    }

    # Append the new test record.
    try:
        file_exists = os.path.exists(csv_filename)
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['testID', 'model', 'testSet', 'guardrails', 'timeTaken', 'date', 'piiPrompt', 'inProgress']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(new_test)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Run tests by calling the headless tester.
    test_results = run_tests_headless(
        selected_csv=test_script,
        selected_model=model,
        prompt_addition=prompt_addition,
        use_guardrails=guard_options.get('guardrailsAI', False),
        use_lakera=guard_options.get('lakeraGuard', False),
        use_presidio=guard_options.get('presidio', False)
    )
    if "error" in test_results:
        return jsonify({'error': test_results["error"]}), 500

    results_df = pd.DataFrame(test_results["results"])
    results_filename = os.path.join(TEST_RESULTS_DIR, f"{test_id}.csv")

    try:
        results_df.to_csv(results_filename, index=False)
    except Exception as e:
        print(f"Error saving results CSV: {e}")

    total_time = test_results.get("total_time", 0)
    # Update the test record with total time and mark as completed.
    update_test_record(csv_filename, test_id, total_time, False)

    return jsonify({
        'message': 'Test completed',
        'data': new_test,
        'total_time': total_time,
        'results_file': f"{test_id}.csv",
        'results': test_results["results"]
    })

if __name__ == '__main__':
    app.run(debug=True)

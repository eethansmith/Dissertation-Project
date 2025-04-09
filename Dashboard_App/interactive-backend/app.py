import os
import csv
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'test-scripts'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Endpoint to get list of tests
@app.route('/api/tests')
def get_tests():
    data = []
    with open('test_list.csv', newline='', encoding='utf-8') as csvfile:
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

    return jsonify(data)


# Endpoint to retrieve available test script names
@app.route('/api/test-scripts')
def get_test_scripts():
    script_folder = app.config['UPLOAD_FOLDER']
    try:
        # List all .csv files in the directory and remove the .csv extension
        files = [f for f in os.listdir(script_folder) if f.endswith('.csv')]
        script_names = [os.path.splitext(f)[0] for f in files]
        return jsonify(script_names)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint for uploading a new test script
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

# New endpoint to start a test and receive all test information.
@app.route('/api/start-test', methods=['POST'])
def start_test():
    data = request.get_json()
    
    # Extract fields from the payload
    model = data.get('model')
    test_script = data.get('testScript')
    pii_prompt = data.get('piiPrompt', '')
    guardrails = data.get('guardrails', {})

    # Convert the guardrail options from boolean values into a list for storage or display.
    guardrails_list = []
    if guardrails.get('guardrailsAI'):
        guardrails_list.append("GuardrailsAI - PII Detection")
    if guardrails.get('lakeraGuard'):
        guardrails_list.append("Lakera Guard - Data Leakage")
    if guardrails.get('presidio'):
        guardrails_list.append("Presidio - PII Detection")
    
    # Get the current date and time for the test
    now = datetime.now()
    date_only_str = now.strftime("%Y-%m-%d")

    # Generate a testID - here we try to read the existing CSV to assign a new unique ID.
    test_id = 1
    csv_filename = 'test_list.csv'
    try:
        if os.path.exists(csv_filename):
            with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                test_ids = [int(row['testID']) for row in reader]
                if test_ids:
                    test_id = max(test_ids) + 1
    except Exception as e:
        # If any error occurs while reading the file, we'll simply start from 1
        test_id = 1

    # Prepare a new test record to be appended to your CSV
    new_test = {
        'testID': test_id,
        'model': model,
        'testSet': test_script,
        'guardrails': ','.join(guardrails_list),
        'timeTaken': 0,  # This can be updated when the test completes
        'date': date_only_str,
        'piiPrompt': pii_prompt,
        'inProgress': True  # This can be used to track if the test is still running
    }

    # Append the new test information to the CSV (create file if it doesn't exist)
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

    # Here you could also initiate the test runs based on the information received.
    # For example, dispatch asynchronous tasks or call other functions here.
    
    return jsonify({'message': 'Test started', 'data': new_test})

if __name__ == '__main__':
    app.run(debug=True)

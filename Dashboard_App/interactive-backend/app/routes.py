# app/routes.py

import os
import csv
import pandas as pd
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
from .tasks import run_in_background
from .config import TEST_RESULTS_DIR

# Import the headless test-run function (if needed at this scope)
# from tester import run_tests_headless

# Create a blueprint
api = Blueprint('api', __name__)

@api.route('/tests', methods=['GET'])
def get_tests():
    data = []
    csv_filename = os.path.join(current_app.root_path, '..', 'test_list.csv')
    try:
        with open(csv_filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    if not row or None in row:
                        current_app.logger.debug("Skipping malformed row: %s", row)
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
                    current_app.logger.error("Skipping row due to error: %s. Row: %s", e, row)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(data)


@api.route('/test-scripts', methods=['GET'])
def get_test_scripts():
    script_folder = current_app.config.get('UPLOAD_FOLDER')
    try:
        files = [f for f in os.listdir(script_folder) if f.endswith('.csv')]
        script_names = [os.path.splitext(f)[0] for f in files]
        return jsonify(script_names)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/upload-test-script', methods=['POST'])
def upload_test_script():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided.'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    filename = secure_filename(file.filename)
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(save_path)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/start-test', methods=['POST'])
def start_test():
    data = request.get_json()

    model = data.get('model')
    # Assuming the front-end sends the script name without the .csv extension.
    test_script = data.get('testScript') + ".csv"
    pii_prompt = data.get('userPrompt', '')
    guardrails = data.get('guardrails', {})

    prompt_addition = pii_prompt if pii_prompt else ""
    guard_options = {
        "guardrailsAI": guardrails.get('guardrailsAI', False),
        "lakeraGuard": guardrails.get('lakeraGuard', False),
        "presidio": guardrails.get('presidio', False)
    }
    guard_list = []
    if guard_options["guardrailsAI"]:
        guard_list.append("GuardrailsAI - PII Detection")
    if guard_options["lakeraGuard"]:
        guard_list.append("Lakera Guard - Data Leakage")
    if guard_options["presidio"]:
        guard_list.append("Presidio - PII Detection")

    now = datetime.now()
    date_only_str = now.strftime("%Y-%m-%d")

    test_id = 1
    csv_filename = os.path.join(current_app.root_path, '..', 'test_list.csv')
    try:
        if os.path.exists(csv_filename):
            with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                test_ids = [int(row['testID']) for row in reader if row.get('testID')]
                if test_ids:
                    test_id = max(test_ids) + 1
    except Exception:
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

    # Run tests in background using the helper function from tasks.py.
    run_in_background(test_id, test_script, model, prompt_addition, guard_options, csv_filename)

    return jsonify({
        'message': 'Test started',
        'testID': test_id,
        'status': 'inProgress'
    }), 202

@api.route('/tests/<int:test_id>', methods=['GET'])
def get_test_results(test_id):
    results_filename = os.path.join("test-dataset", f"{test_id}.csv")
    test_list_filename = os.path.join(current_app.root_path, '..', 'test_list.csv')

    if not os.path.exists(results_filename):
        return jsonify({'error': 'Test results not found'}), 404

    try:
        df_results = pd.read_csv(results_filename)
        results_list = df_results.to_dict(orient='records')

        metadata = {}
        if os.path.exists(test_list_filename):
            with open(test_list_filename, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if int(row.get('testID', -1)) == test_id:
                        metadata = {
                            'model': row.get('model', ''),
                            'prompt': row.get('piiPrompt', ''),
                            'guardrails': row.get('guardrails', '')
                        }
                        break

        return jsonify({
            'metadata': metadata,
            'results': results_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

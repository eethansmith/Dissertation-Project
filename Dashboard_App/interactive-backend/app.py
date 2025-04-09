import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'test-scripts'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/tests')
def get_tests():
    data = []
    with open('test_list.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['testID'] = int(row['testID'])
            row['timeTaken'] = int(row['timeTaken'])
            row['guardrails'] = row['guardrails'].split(',') if row['guardrails'] else []
            data.append(row)
    return jsonify(data)

@app.route('/api/test-scripts')
def get_test_scripts():
    script_folder = app.config['UPLOAD_FOLDER']
    try:
        # List all .csv files in the directory
        files = [f for f in os.listdir(script_folder) if f.endswith('.csv')]
        # Strip the .csv extension
        script_names = [os.path.splitext(f)[0] for f in files]
        return jsonify(script_names)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New endpoint for file upload 
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

if __name__ == '__main__':
    app.run(debug=True)

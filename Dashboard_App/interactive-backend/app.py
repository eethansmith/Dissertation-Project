from flask import Flask, jsonify
from flask_cors import CORS
import csv

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(debug=True)

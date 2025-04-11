# app/config.py

import os

# Base directory (if needed for absolute path resolution)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'test-scripts')
TEST_RESULTS_DIR = os.path.join(BASE_DIR, '..', 'test-dataset')

# Other configuration parameters can be added here
DEBUG = True

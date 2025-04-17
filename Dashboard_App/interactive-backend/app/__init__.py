# app/__init__.py

import os
from flask import Flask
from flask_cors import CORS
from .config import UPLOAD_FOLDER, DEBUG, TEST_RESULTS_DIR

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Set configuration values
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['DEBUG'] = DEBUG

    # Ensure required directories exist.
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(TEST_RESULTS_DIR, exist_ok=True)

    # Register blueprints.
    from .routes import api
    app.register_blueprint(api, url_prefix='/api')

    return app

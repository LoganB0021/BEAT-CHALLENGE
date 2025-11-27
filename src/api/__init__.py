# api/__init__.py
from flask import Flask
from flask_cors import CORS
from api.config import Config
from api.blueprints import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Register all blueprints
    register_blueprints(app)

    return app

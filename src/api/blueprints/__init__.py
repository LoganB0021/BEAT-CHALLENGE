# app/blueprints/__init__.py

from .challenge import challenge_bp

def register_blueprints(app):
    app.register_blueprint(challenge_bp, url_prefix="/api/challenge")

import os

from flask import Flask
from flask_cors import CORS

from api.config import Config
from api.routes import api_blueprint


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or Config)
    if app.config.get("TRUSTED_HOSTS"):
        app.config["TRUSTED_HOSTS"] = app.config["TRUSTED_HOSTS"]

    origins = app.config.get("ALLOWED_ORIGINS", [])
    if origins:
        CORS(
            app,
            resources={
                r"/api/*": {
                    "origins": origins,
                    "methods": ["GET", "POST"],
                    "allow_headers": ["Authorization", "Content-Type"],
                    "expose_headers": ["Content-Disposition"],
                }
            },
        )

    app.register_blueprint(api_blueprint, url_prefix="/api")
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")

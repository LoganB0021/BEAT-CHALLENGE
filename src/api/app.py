from flask import Flask
from flask_cors import CORS
from api.config import Config
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS (allows frontend to talk to backend)
CORS(app)

# Register API routes
# app.register_blueprint(api_blueprint, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True)

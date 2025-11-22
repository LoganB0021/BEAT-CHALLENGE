from flask import Blueprint, jsonify
from beat_challenge_generator.file_selector import generate_beat_challenge

# Define API Blueprint
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/daily-challenge', methods=['GET'])
def get_daily_challenge():
    """API route to fetch the daily beat challenge."""
    challenge = generate_beat_challenge()
    return jsonify({"challenge": challenge})

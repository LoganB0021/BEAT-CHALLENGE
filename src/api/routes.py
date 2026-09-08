import os

from flask import Blueprint, jsonify, request, send_file
from beat_challenge_generator.challenge_service import generate_challenge
from beat_challenge_generator.db import get_session, init_db

# Define API Blueprint
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/daily-challenge', methods=['GET'])
def get_daily_challenge():
    """Return the stored daily challenge or generate a random challenge."""
    mode = request.args.get("mode", "daily")

    init_db()
    try:
        with get_session() as db:
            pack = generate_challenge(db, mode=mode)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not pack:
        return jsonify({"error": "No indexed sounds are available."}), 404

    return send_file(
        pack.zip_path,
        as_attachment=True,
        download_name=os.path.basename(pack.zip_path),
        mimetype="application/zip",
    )

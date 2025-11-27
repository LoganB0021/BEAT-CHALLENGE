from datetime import date
from flask import Blueprint, send_file
from beat_challenge_generator.services.file_selector import deterministic_select_by_date
from beat_challenge_generator.services.file_manager import create_pack
from beat_challenge_generator.db.session import get_session
from beat_challenge_generator.logging.logger import logger

challenge_bp = Blueprint("challenge", __name__, url_prefix="/api/challenge")

@challenge_bp.get("/today")
def get_today_challenge():
    target_date = date.today()
    with get_session() as session:
        selected = deterministic_select_by_date(session, target_date)
        zip_path = create_pack(selected, session)
        logger.info(f"Pack created at: {zip_path}")
        
        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name="today_challenge.zip"
        )


import hmac
import os

from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, render_template, request, send_file, url_for

from beat_challenge_generator.challenge_service import generate_challenge
from beat_challenge_generator.db import get_session
from beat_challenge_generator.jobs import create_job, hash_api_key, reserve_job_slot
from beat_challenge_generator.models import ChallengeJob, Pack


api_blueprint = Blueprint("api", __name__)
web_blueprint = Blueprint("web", __name__)


@web_blueprint.route("/", methods=["GET"])
def landing_page():
    response = current_app.make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


def _require_random_api_key():
    return _require_api_key("random challenges are not configured")


def _require_api_key(missing_message):
    configured_key = current_app.config.get("BEAT_API_KEY")
    if not configured_key:
        return jsonify({"error": missing_message}), 503

    authorization = request.headers.get("Authorization", "")
    scheme, _, supplied_key = authorization.partition(" ")
    if scheme.lower() != "bearer" or not supplied_key:
        return jsonify({"error": "authentication required"}), 401
    if not hmac.compare_digest(supplied_key, configured_key):
        return jsonify({"error": "authentication required"}), 401
    return None


def _authorized_job(job, supplied_key):
    return job.api_key_hash == hash_api_key(supplied_key)


@api_blueprint.route("/daily-challenge", methods=["GET"])
def get_daily_challenge():
    mode = request.args.get("mode", "daily")

    if mode not in {"daily", "random"}:
        return jsonify({"error": "mode must be 'daily' or 'random'"}), 400
    if mode == "random" and not current_app.config.get("ALLOW_RANDOM_CHALLENGES", False):
        return jsonify({"error": "random challenges are disabled"}), 403
    if mode == "random":
        auth_error = _require_random_api_key()
        if auth_error:
            return auth_error

    try:
        with get_session() as db:
            pack = generate_challenge(db, mode=mode)
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 409
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if not pack:
        return jsonify({"error": "No indexed sounds are available."}), 404

    response = send_file(
        pack.zip_path,
        as_attachment=True,
        download_name=os.path.basename(pack.zip_path),
        mimetype="application/zip",
        max_age=0,
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@api_blueprint.route("/challenges", methods=["POST"])
def create_challenge_job():
    if not current_app.config.get("ALLOW_ASYNC_CHALLENGES", False):
        return jsonify({"error": "asynchronous challenges are disabled"}), 503

    auth_error = _require_api_key("asynchronous challenges are not configured")
    if auth_error:
        return auth_error

    payload = request.get_json(silent=True)
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        return jsonify({"error": "request body must be a JSON object"}), 400
    mode = payload.get("mode", "random")
    if mode not in {"daily", "random"}:
        return jsonify({"error": "mode must be 'daily' or 'random'"}), 400
    if mode == "random" and not current_app.config.get("ALLOW_RANDOM_CHALLENGES", False):
        return jsonify({"error": "random challenges are disabled"}), 403

    configured_key = current_app.config["BEAT_API_KEY"]
    with get_session() as db:
        if not reserve_job_slot(
            db,
            configured_key,
            window_seconds=current_app.config["JOB_RATE_LIMIT_SECONDS"],
            limit=current_app.config["MAX_JOBS_PER_RATE_WINDOW"],
        ):
            return jsonify({"error": "challenge generation rate limit exceeded"}), 429
        job = create_job(db, mode=mode, api_key=configured_key)

    return (
        jsonify(
            {
                "id": job.id,
                "mode": job.mode,
                "status": job.status,
                "status_url": url_for("api.get_challenge_job", job_id=job.id),
            }
        ),
        202,
    )


@api_blueprint.route("/challenges/<job_id>", methods=["GET"])
def get_challenge_job(job_id):
    auth_error = _require_api_key("asynchronous challenges are not configured")
    if auth_error:
        return auth_error

    configured_key = current_app.config["BEAT_API_KEY"]
    with get_session() as db:
        job = db.get(ChallengeJob, job_id)
        if not job or not _authorized_job(job, configured_key):
            return jsonify({"error": "challenge job not found"}), 404

        payload = {
            "id": job.id,
            "mode": job.mode,
            "status": job.status,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        }
        if job.status == "completed" and job.pack_id:
            pack = db.get(Pack, job.pack_id)
            if pack and pack.zip_path and os.path.isfile(pack.zip_path):
                payload["download_url"] = url_for("api.get_challenge_pack", job_id=job.id)
        if job.status == "failed":
            payload["error"] = "challenge generation failed"
        return jsonify(payload)


@api_blueprint.route("/challenges/<job_id>/download", methods=["GET"])
def get_challenge_pack(job_id):
    auth_error = _require_api_key("asynchronous challenges are not configured")
    if auth_error:
        return auth_error

    configured_key = current_app.config["BEAT_API_KEY"]
    with get_session() as db:
        job = db.get(ChallengeJob, job_id)
        if not job or not _authorized_job(job, configured_key) or job.status != "completed":
            return jsonify({"error": "completed challenge not found"}), 404
        pack = db.get(Pack, job.pack_id)
        if not pack or not pack.zip_path:
            return jsonify({"error": "completed challenge not found"}), 404

        response = send_file(
            pack.zip_path,
            as_attachment=True,
            download_name=os.path.basename(pack.zip_path),
            mimetype="application/zip",
            max_age=0,
        )
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

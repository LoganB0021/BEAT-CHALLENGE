import zipfile
from io import BytesIO

from beat_challenge_generator import jobs


def test_landing_page_links_to_daily_challenge(api_app):
    response = api_app().test_client().get("/")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    assert "Make something" in response.get_data(as_text=True)
    assert "/api/daily-challenge" in response.get_data(as_text=True)
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_daily_api_returns_zip_with_safety_headers(
    api_app, ingested_assets
):
    client = api_app().test_client()
    response = client.get("/api/daily-challenge")

    assert response.status_code == 200
    assert response.mimetype == "application/zip"
    assert response.headers["Cache-Control"] == "no-store"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    with zipfile.ZipFile(BytesIO(response.data)) as archive:
        assert archive.namelist()


def test_daily_api_reports_empty_index(api_app):
    response = api_app().test_client().get("/api/daily-challenge")
    assert response.status_code == 404
    assert response.get_json()["error"] == "No indexed sounds are available."


def test_daily_api_rejects_invalid_mode(api_app):
    response = api_app().test_client().get("/api/daily-challenge?mode=weekly")
    assert response.status_code == 400
    assert "mode must" in response.get_json()["error"]


def test_random_api_requires_bearer_auth(api_app, ingested_assets):
    client = api_app(
        ALLOW_RANDOM_CHALLENGES=True, BEAT_API_KEY="secret"
    ).test_client()
    assert client.get("/api/daily-challenge?mode=random").status_code == 401
    assert (
        client.get(
            "/api/daily-challenge?mode=random",
            headers={"Authorization": "Bearer wrong"},
        ).status_code
        == 401
    )
    response = client.get(
        "/api/daily-challenge?mode=random",
        headers={"Authorization": "Bearer secret"},
    )
    assert response.status_code == 200


def test_async_api_validates_json_and_mode(api_app):
    client = api_app(
        ALLOW_ASYNC_CHALLENGES=True, BEAT_API_KEY="secret"
    ).test_client()
    auth = {"Authorization": "Bearer secret"}
    assert client.post("/api/challenges", json=["random"], headers=auth).status_code == 400
    assert (
        client.post(
            "/api/challenges", json={"mode": "weekly"}, headers=auth
        ).status_code
        == 400
    )


def test_cors_allows_configured_origin(api_app, ingested_assets):
    client = api_app(ALLOWED_ORIGINS=["https://client.example"]).test_client()
    response = client.get(
        "/api/daily-challenge",
        headers={"Origin": "https://client.example"},
    )
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "https://client.example"


def test_cors_preflight_allows_async_headers(api_app):
    client = api_app(ALLOWED_ORIGINS=["https://client.example"]).test_client()
    response = client.options(
        "/api/challenges",
        headers={
            "Origin": "https://client.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization, Content-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "https://client.example"
    assert "POST" in response.headers["Access-Control-Allow-Methods"]
    assert "Authorization" in response.headers["Access-Control-Allow-Headers"]


def test_async_job_submission_status_and_download(
    api_app, ingested_assets, session_factory
):
    app = api_app(
        ALLOW_ASYNC_CHALLENGES=True,
        BEAT_API_KEY="secret",
        JOB_RATE_LIMIT_SECONDS=60,
        MAX_JOBS_PER_RATE_WINDOW=2,
    )
    client = app.test_client()
    auth = {"Authorization": "Bearer secret"}
    queued = client.post("/api/challenges", json={"mode": "daily"}, headers=auth)
    assert queued.status_code == 202
    payload = queued.get_json()
    assert payload["status"] == "pending"

    pending = client.get(f"/api/challenges/{payload['id']}", headers=auth)
    assert pending.status_code == 200
    assert pending.get_json()["status"] == "pending"

    with session_factory() as db:
        job = jobs.claim_next_job(db)
        jobs.process_job(db, job)

    completed = client.get(f"/api/challenges/{payload['id']}", headers=auth)
    assert completed.status_code == 200
    result = completed.get_json()
    assert result["status"] == "completed"
    download = client.get(result["download_url"], headers=auth)
    assert download.status_code == 200
    assert download.mimetype == "application/zip"


def test_completed_job_without_archive_has_no_download_url(
    api_app, ingested_assets, session_factory
):
    app = api_app(ALLOW_ASYNC_CHALLENGES=True, BEAT_API_KEY="secret")
    client = app.test_client()
    auth = {"Authorization": "Bearer secret"}
    queued = client.post("/api/challenges", json={"mode": "daily"}, headers=auth)

    with session_factory() as db:
        job = jobs.claim_next_job(db)
        jobs.process_job(db, job)
        from beat_challenge_generator.models import Pack

        pack = db.get(Pack, job.pack_id)
        import os

        os.remove(pack.zip_path)

    status = client.get(f"/api/challenges/{queued.get_json()['id']}", headers=auth)
    assert status.status_code == 200
    assert "download_url" not in status.get_json()


def test_async_job_quota_returns_429(api_app):
    client = api_app(
        ALLOW_ASYNC_CHALLENGES=True,
        BEAT_API_KEY="secret",
        JOB_RATE_LIMIT_SECONDS=60,
        MAX_JOBS_PER_RATE_WINDOW=1,
    ).test_client()
    auth = {"Authorization": "Bearer secret"}
    assert (
        client.post(
            "/api/challenges", json={"mode": "daily"}, headers=auth
        ).status_code
        == 202
    )
    assert (
        client.post(
            "/api/challenges", json={"mode": "daily"}, headers=auth
        ).status_code
        == 429
    )

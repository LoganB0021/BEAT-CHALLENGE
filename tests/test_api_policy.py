from api.app import create_app


class PolicyConfig:
    TESTING = True
    SECRET_KEY = "test"
    ALLOWED_ORIGINS = []
    ALLOW_RANDOM_CHALLENGES = False
    ALLOW_ASYNC_CHALLENGES = False
    BEAT_API_KEY = None
    TRUSTED_HOSTS = None
    MAX_CONTENT_LENGTH = 16 * 1024


def test_random_generation_is_disabled_by_default():
    client = create_app(PolicyConfig).test_client()
    response = client.get("/api/daily-challenge?mode=random")
    assert response.status_code == 403


def test_async_generation_is_disabled_by_default():
    client = create_app(PolicyConfig).test_client()
    response = client.post("/api/challenges", json={"mode": "random"})
    assert response.status_code == 503

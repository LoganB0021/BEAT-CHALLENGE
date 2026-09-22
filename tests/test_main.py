from click.testing import CliRunner

from beat_challenge_generator import main as main_module


def test_main_passes_overwrite_to_generation(monkeypatch):
    calls = {}

    class SessionContext:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_generate(db, **kwargs):
        calls.update(kwargs)
        return type("Pack", (), {"zip_path": "/tmp/daily_2026-09-22.zip"})()

    monkeypatch.setattr(main_module, "get_session", lambda: SessionContext())
    monkeypatch.setattr(main_module, "generate_challenge", fake_generate)

    result = CliRunner().invoke(main_module.main, ["--mode", "daily", "--overwrite"])

    assert result.exit_code == 0
    assert calls == {"mode": "daily", "overwrite": True}
    assert "daily_2026-09-22.zip" in result.output

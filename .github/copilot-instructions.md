# Copilot / AI Assistant Instructions for BEAT-CHALLENGE

This repository is a Python project for generating deterministic or random beat challenge packs from files stored under `beats/`, indexing them in SQLite, and packaging the chosen selections into ZIP archives.

## Build, test, and validation commands

Use `uv` for project setup and execution; this repository's README and `pyproject.toml` are written around it.

- Install dependencies:
  - `uv sync`
- Create a venv if needed:
  - `uv venv`
- Run the CLI generator:
  - `uv run beat-gen --mode daily`
  - `uv run beat-gen --mode random`
- Ingest/refresh the database index from the filesystem:
  - `uv run python -m beat_challenge_generator.ingest`
  - `uv run python -m beat_challenge_generator.ingest --dry-run`
  - `uv run python -m beat_challenge_generator.ingest --category fx`
- Run the API locally:
  - `export PYTHONPATH=src && uv run python -m api.app`
  - `curl -f -OJ http://localhost:5000/api/daily-challenge`
- Run tests:
  - `uv run pytest tests/`
  - `uv run pytest tests/test_config.py -q`
  - `uv run pytest tests/test_file_selector.py -q`
  - `uv run pytest tests/test_ingest.py -q`

There is no dedicated lint tool configured in `pyproject.toml`; the project validation path is the pytest suite. If you add linting later, keep it project-scoped and document the command here.

## High-level architecture

The project has three main layers:

- `src/beat_challenge_generator/` contains the core logic.
  - `config.py` defines paths (`BEAT_DIR`, `OUTPUT_DIR`, `PACKS_DIR`, `DATA_DIR`) and creates the required directories at import time.
  - `db.py` configures SQLAlchemy and the SQLite engine; `init_db()` creates the tables.
  - `models.py` defines the `Sound` and `Pack` ORM models; `Sound.file_path` is derived from `beats/<category>/<relative_path>`.
  - `ingest.py` scans `beats/` and upserts indexed `Sound` rows with checksum and size metadata.
  - `file_selector.py` chooses a random or date-seeded item per category from the DB.
  - `challenge_service.py` is the shared orchestration layer that selects, packages, and persists a challenge.
  - `file_manager.py` writes the ZIP archive to `output/packs/` and records metadata in the `packs` table.
  - `main.py` is the CLI entry point.
- `src/api/` exposes the Flask API.
  - `app.py` creates the Flask app and registers the blueprint.
  - `routes.py` serves `/api/daily-challenge` and delegates to `generate_challenge()`.
- `data/` stores the SQLite database and `output/packs/` stores generated archives.

The important data flow is: source files in `beats/` -> ingest DB -> deterministic/random selection -> `create_pack()` -> persisted `Pack` record + ZIP archive.

## Key repository conventions

- Category names are fixed and significant: `drum_kits`, `fx`, and `samples`.
- `beats/` is the source of truth; do not select directly from the filesystem in new code paths unless the existing workflow requires it. The project is designed to select from the indexed database after `ingest` runs.
- `Sound.relative_path` is unique per category and is used to reconstruct each item's absolute path. Directory-based drum kits are treated as a single `Sound` row with `is_folder=True`; nested files are included recursively when the ZIP is built.
- Directory creation is intentionally side-effectful: importing `config.py` and related modules creates `beats/*`, `output/`, `data/`, and `logs/` as needed. Tests depend on this behavior.
- Logging is centralized through the `logger` configured in `beat_challenge_generator.logger`; avoid replacing or reconfiguring it globally in feature work.
- The default database URL is SQLite under `data/beat_challenge.db` and can be overridden with `DATABASE_URL`.
- On PythonAnywhere Developer, MySQL is the practical server-database upgrade; the SQLAlchemy engine uses `pool_recycle=280` and `pool_pre_ping=True` for MySQL.
- Random API generation is disabled by default and, when enabled, requires `BEAT_API_KEY` as a Bearer token.
- Long-running generation uses the opt-in `POST /api/challenges` job API and `beat-worker`; configure only one worker under PythonAnywhere Developer's single always-on task.
- The archive names are time-based and stored in `output/packs/`; the DB stores the generated `Pack` record with metadata such as `date`, `checksum`, `size_bytes`, and `items`.

## Practical guidance for edits

- To change selection semantics, work in `src/beat_challenge_generator/file_selector.py` or `src/beat_challenge_generator/challenge_service.py`.
- To change packaging behavior or ZIP structure, edit `src/beat_challenge_generator/file_manager.py`.
- To add or change API behavior, update `src/api/routes.py` and the blueprint setup in `src/api/app.py`.
- To change database schema or model semantics, update `src/beat_challenge_generator/models.py` and keep migrations/DB initialization in sync.
- Before adding new repository-level commands, prefer matching the existing `uv run ...` workflow used by the project instead of introducing ad hoc shells or `pip` commands.
- Do not add Flask background threads for hosted work. PythonAnywhere Developer has one always-on task; long-running generation should use a durable database-backed job workflow rather than process-local state.

## Repository-specific notes

- `README.md` is the primary user-facing guide and should be treated as the source of truth for setup and CLI examples.
- The project uses SQLite by default; tests assume the repo can create the needed directories and DB files locally.
- If a task changes the ingest or selection contract, also update the tests under `tests/` and validate with the smallest relevant pytest target.

If you need examples of project-specific changes, the most common extension points are the DB-backed selection flow, pack ZIP generation, and the Flask route layer.

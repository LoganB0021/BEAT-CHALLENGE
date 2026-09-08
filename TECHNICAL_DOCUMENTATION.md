# Beat Challenge Generator: Technical Documentation

This document is an implementation guide for developers working on the Beat Challenge Generator. It describes the current code paths, data contracts, local setup, and extension points.

## 1. System Overview

The project selects beat components from `beats/`, packages them into ZIP archives, and optionally records indexed sounds and generated packs in SQLite through SQLAlchemy.

There is one shared generation workflow with two modes:

| Mode | Selection | Output | Database record |
| --- | --- | --- | --- |
| `daily` | Deterministic selection from `Sound` rows using the target date | `output/packs/pack_<timestamp>.zip` | Yes, through `Pack`; one record per date |
| `random` | Random item from each category's `Sound` rows | `output/packs/pack_<timestamp>.zip` | Yes, through `Pack` |

The shared workflow lives in `challenge_service.generate_challenge`. Both the API and CLI open a SQLAlchemy session, call that method, and receive a persisted `Pack` object. The API streams `Pack.zip_path`; the CLI prints it.

## 2. Repository Layout

```text
beats/                         Source beat content
  drum_kits/                    Drum kits; files or folders are supported
  fx/                           FX files or folders
  samples/                      Sample files or folders

src/beat_challenge_generator/  Core package
  config.py                    Paths, category names, directory initialization
  db.py                        SQLAlchemy engine, sessions, table initialization
  models.py                    Sound and Pack ORM models
  ingest.py                    Scans beats/ and upserts Sound records
  file_selector.py             Random and deterministic selection logic
  file_manager.py              ZIP creation
  logger.py                    Loguru configuration and retention
  main.py                      CLI orchestration for database-backed packs

src/api/                       Flask application
  app.py                       Flask app creation and blueprint registration
  config.py                    Flask configuration
  routes.py                    HTTP endpoint implementations

data/                          SQLite database by default
output/                         Generated files
  packs/                       Database-backed CLI packs
logs/                           Rotating application logs
tests/                          Pytest test suite
pyproject.toml                 Package metadata and dependencies
uv.lock                        Locked dependency versions
```

## 3. Local Setup

Requirements:

- Python 3.12 or newer supported by the local environment
- [uv](https://docs.astral.sh/uv/)

Create the environment and install dependencies:

```sh
uv venv
uv sync
```

For Linux/macOS, activate the environment when desired:

```sh
source .venv/bin/activate
```

The package can also be run through `uv run`, which does not require manual activation.

## 4. Important Configuration

`src/beat_challenge_generator/config.py` derives paths from the repository root:

- `BEAT_DIR`: `beats/`
- `OUTPUT_DIR`: `output/`
- `PACKS_DIR`: `output/packs/`
- `DATA_DIR`: `data/`
- `BEAT_SUBDIRS`: `drum_kits`, `fx`, `samples`

These directories and category folders are created during import. This import-time side effect is relied upon by the existing tests and runtime commands.

### Database URL

Set `DATABASE_URL` to override the default SQLite database:

```sh
export DATABASE_URL=sqlite:////absolute/path/to/beat_challenge.db
```

The default used by the core package is:

```text
sqlite:///data/beat_challenge.db
```

A SQLAlchemy-compatible database URL can be used for another database engine, provided its driver is installed and the models are compatible with that engine.

## 5. Beat Content Contract

The selector and ingester expect these category directories:

```text
beats/drum_kits/
beats/fx/
beats/samples/
```

A category item can be either a file or an immediate child directory. Drum kits commonly use directories, and directory contents are recursively included in generated ZIPs.

After adding or changing content, update the database index before using the CLI path:

```sh
uv run python -m beat_challenge_generator.ingest
```

The ingester scans only immediate children of each category directory. A directory is stored as one `Sound` item; its nested files are not stored as separate selectable items.

## 6. Ingestion Pipeline

The main function is `beat_challenge_generator.ingest.ingest_beats`.

For each category item, it:

1. Determines whether the item is a file or directory.
2. Computes a SHA-256 checksum and total byte size.
3. Looks up an existing row by `category` and `relative_path`.
4. Inserts a new `Sound` row or updates checksum, size, and folder status.
5. Commits once after all categories are processed.

Useful commands:

```sh
# Scan and commit all categories
uv run python -m beat_challenge_generator.ingest

# Report changes without committing
uv run python -m beat_challenge_generator.ingest --dry-run

# Limit the scan to one category
uv run python -m beat_challenge_generator.ingest --category fx
```

The ingest operation is intended to be idempotent. Running it repeatedly without changing source files should report items as unchanged.

## 7. Selection and Packaging

### Challenge modes

`challenge_service.generate_challenge(db, mode=...)` is the public application workflow. It selects `Sound` rows, packages them, persists a `Pack`, and returns that record.

For `daily`, it calls `file_selector.deterministic_select_by_date()`. The same date always selects the same indexed sounds, and an existing archive is reused unless overwrite is requested.

For `random`, it calls `challenge_service.random_select()`, which uses `random.choice` on each category's indexed `Sound` rows. Random packs are also persisted, with a unique timestamp-based date key. Public random generation is disabled by default and should be protected by `BEAT_API_KEY`.

Both modes package `Sound` objects through `file_manager.create_pack()`. No API or CLI path selects directly from the filesystem.

The selection result has the shape:

```python
{
  "drum_kits": Sound(...),
  "fx": Sound(...),
  "samples": Sound(...),
}
```

`file_manager.create_pack()` resolves each item below `BEAT_DIR`, writes a ZIP under `PACKS_DIR`, computes the archive checksum, and stores the `Pack` record. The ZIP contains paths prefixed by category, for example:

```text
drum_kits/bankroll 808/808 (1).wav
fx/reverb.wav
samples/texture.mp3
```

The CLI orchestration is in `main.main()` and uses the same service as the API:

```sh
uv run beat-gen --mode daily
uv run beat-gen --mode random
```

Daily mode always reuses today's existing database record. Random mode creates and stores a new pack on each invocation. Regeneration remains available only to internal callers of `generate_challenge(..., overwrite=True)`; it is intentionally not exposed through the API or CLI.

## 8. Data Model

### `Sound`

Defined in `src/beat_challenge_generator/models.py`:

| Field | Meaning |
| --- | --- |
| `id` | Primary key |
| `name` | Item basename |
| `category` | Category such as `drum_kits`, `fx`, or `samples` |
| `relative_path` | Path relative to the category directory |
| `is_folder` | Whether the selected item is a directory |
| `checksum` | SHA-256 checksum of the file or directory contents |
| `size_bytes` | File size or recursive directory size |
| `tags` | Optional JSON metadata |
| `created_at` / `updated_at` | Timestamp fields |

`Sound.file_path` derives the absolute path from `BEAT_DIR`, `category`, and `relative_path`.

### `Pack`

A generated database-backed pack contains:

- `name`: logical pack name, currently `pack_YYYY-MM-DD`
- `date`: unique challenge date
- `seed`: date-based selection seed
- `zip_path`: generated archive path
- `size_bytes`: archive size
- `checksum`: SHA-256 checksum of the archive
- `items`: JSON list of selected `Sound` IDs
- `status`: currently `generated`
- `generated_by`: currently `file_selector`
- `created_at` / `updated_at`: timestamps

## 9. HTTP API

Start the development server from the repository root:

```sh
export PYTHONPATH=src
uv run python -m api.app
```

The Flask app registers the API blueprint under `/api`.

### `GET /api/daily-challenge`

The endpoint:

1. Opens the shared database session.
2. Calls `challenge_service.generate_challenge()` in `daily` mode by default.
3. Reuses today's stored `Pack`, or creates it if it does not exist.
4. Returns `Pack.zip_path` as an attachment with `Content-Type: application/zip`.

Query parameters:

| Parameter | Values | Default | Meaning |
| --- | --- | --- | --- |
| `mode` | `daily`, `random` | `daily` | Select deterministic daily or opt-in random indexed sounds |

Example request:

```sh
curl -f -OJ http://localhost:5000/api/daily-challenge
```

Successful responses have a `Content-Disposition` header similar to:

```text
attachment; filename=pack_20260906_221943.zip
```

Random mode is disabled unless `ALLOW_RANDOM_CHALLENGES=true` and
`BEAT_API_KEY` is configured. When enabled, send the key as a Bearer token:

```sh
curl -f -OJ \
  -H "Authorization: Bearer $BEAT_API_KEY" \
  'http://localhost:5000/api/daily-challenge?mode=random'
```

An unsupported mode returns HTTP `400`.

### Asynchronous challenge jobs

For generation that should not occupy a web worker, enable
`ALLOW_ASYNC_CHALLENGES=true`, initialize the `challenge_jobs` table with
`beat-init-db`, and run exactly one `beat-worker` process under the
PythonAnywhere Developer always-on task.

Submit a job:

```sh
curl -X POST \
  -H "Authorization: Bearer $BEAT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"mode":"random"}' \
  http://localhost:5000/api/challenges
```

The API returns `202` with an ID and status URL. Poll
`GET /api/challenges/<id>` using the same Bearer token; once the status is
`completed`, download from the returned `download_url`. Jobs are rate limited
by the configured API key using `JOB_RATE_LIMIT_SECONDS` and
`MAX_JOBS_PER_RATE_WINDOW`.

The request body must be a JSON object. Invalid JSON shapes return `400`.
Browser clients configured through `ALLOWED_ORIGINS` may submit the `POST`
request with `Authorization` and `Content-Type` headers; other origins are
not granted API CORS access.

If no indexed sounds are available, the route returns HTTP `404` with:

```json
{"error": "Could not create the daily challenge pack."}
```

When adding an endpoint, place the route in `src/api/routes.py`. The blueprint is already registered by `src/api/app.py`; use the existing blueprint unless a separate API version or module is needed.

## 10. Logging

`src/beat_challenge_generator/logger.py` configures Loguru at import time. Runtime activity is written to `logs/` with rotation at 5 MB and retention of the last five log files.

Use the shared logger:

```python
from beat_challenge_generator.logger import logger

logger.info("Pack created")
logger.warning("Source file is missing")
logger.error("Pack creation failed")
```

Avoid reconfiguring the global logger in individual modules.

## 11. Testing Workflow

Run the full suite:

```sh
uv run pytest tests/
```

Run a focused test file:

```sh
uv run pytest tests/test_file_selector.py -v
```

For API changes, a lightweight Flask client check is useful:

```sh
PYTHONPATH=src uv run python -c 'from api.app import app; response = app.test_client().get("/api/daily-challenge"); print(response.status_code, response.content_type)'
```

When testing code that imports `config.py` or `logger.py`, remember that those modules create directories and configure logging during import.

## 12. Development Guidelines

- Keep category names consistent with `BEAT_SUBDIRS`; they are used as database values, filesystem directories, and ZIP prefixes.
- Use `relative_path` for paths inside a category. Do not introduce a second path convention without updating ingestion, selection, and packaging together.
- Preserve folder support when changing ZIP behavior.
- Use the shared logger rather than creating a new logger configuration.
- Prefer deterministic behavior for database-backed workflows and explicit randomness for the API workflow.
- Add or update focused tests when changing selection, ingestion, ZIP layout, or route response behavior.
- Do not commit generated ZIPs, logs, virtual environments, or local database files unless the project explicitly needs a fixture.

## 13. Recommended Extension Points

### Add a new category

Update all of the following as one change:

1. `BEAT_SUBDIRS` in `config.py`.
2. Category lists in `file_selector.py`.
3. Any tests and sample fixtures.
4. Documentation and ZIP layout expectations.

Then run ingestion so the new category has `Sound` records.

### Make the API deterministic

Replace the random API selector with a database-backed selection flow using `get_session()` and `deterministic_select_by_date()`. Decide whether API-generated packs should also create `Pack` records, and keep the response contract as a file download.

### Add pack metadata without changing the download

Use response headers such as `X-Pack-Checksum` or a separate metadata endpoint. Avoid embedding metadata in the ZIP unless clients need it as a file.

## 14. Known Implementation Details

- The API and CLI now use the same database-backed service and archive location.
- Daily requests reuse the existing `Pack` record for the date; random requests create a new persisted pack.
- Both modes rely on ingested `Sound` rows. An empty or stale database can result in missing categories or an empty selection.
- The core package and Flask app each have configuration modules; use `beat_challenge_generator.config` for generator paths and `api.config` for Flask settings.
- Several modules perform setup during import, so import order can affect directory and database initialization in tests.

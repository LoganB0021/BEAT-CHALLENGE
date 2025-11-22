# Copilot / AI Assistant Instructions for BEAT-CHALLENGE

Concise, codebase-specific notes to help an AI assistant be productive in this repository.

**Quick Orientation**
- Purpose: Randomly select beat components (drum kits, FX, samples), package them as a zip, and log the operation.
- Core runtime pieces live under `src/beat_challenge_generator/` and a small API exists under `src/api/`.

**How to run (developer flow)**
- Create a virtualenv and install in editable mode: `python -m venv venv` then `venv\Scripts\activate` and `pip install -e .`.
- Generate a beat from the CLI: `python -m beat_challenge_generator.main` (runs `main()` which selects files, zips them, and logs results).
- Run the HTTP API (dev): ensure Python can import packages from `src` or install editable. Example (PowerShell):
  - `$env:PYTHONPATH='src'; python -m api.app`
  - This starts Flask and registers the blueprint at `/api`; the route of interest is `GET /api/daily-challenge`.
- Tests: `pytest tests/` (or `pytest -v`). Running `pip install -e .` before tests avoids import path issues.

**High-level architecture & data flow**
- `beat_challenge_generator/config.py` — sets `BASE_DIR`, `BEAT_DIR`, `OUTPUT_DIR`, and ensures directories exist. It's imported early by `main.py`.
- `beat_challenge_generator/logger.py` — initializes `loguru` logger, creates `logs/`, rotates at 5 MB, and **keeps only the last 5 logs**. It runs cleanup at import time.
- `beat_challenge_generator/file_selector.py` — selects one item per category. Categories are hard-coded: `['drum_kits', 'fx', 'samples']`. Drum kits can be a folder (preserves folder in zip).
- `beat_challenge_generator/file_manager.py` — receives the `selected_files` dict and creates a zip in `output/`. When adding a directory it preserves the relative path under `beats/`.
- `beat_challenge_generator/main.py` — orchestrates selection, packaging, and logging.
- `src/api/app.py` + `src/api/routes.py` — simple Flask app + blueprint that calls `generate_beat_challenge()` and returns JSON.

**Patterns & repository conventions**
- Directory names are important and used as keys: `beats/drum_kits`, `beats/fx`, `beats/samples`.
- Files vs folders: `drum_kits` explicitly supports folders; code expects either files or directories. When handling a directory, `file_manager.add_to_zip` will walk and include all files.
- Logging: use the `logger` exported by `beat_challenge_generator.logger` (already configured to write to `logs/`). Avoid reconfiguring loggers globally; append where necessary.
- Initialization by import: `config.py` and `logger.py` perform side-effects (create directories, create log file). Imports should be done intentionally early in a run to ensure directories exist.

**Common edits & where to make them (examples)**
- Change selection logic: edit `src/beat_challenge_generator/file_selector.py` (categories are defined there).
- Change how packs are built/structured in the zip: edit `src/beat_challenge_generator/file_manager.py` (see `add_to_zip` to preserve folder structure).
- Change log retention/format: edit `src/beat_challenge_generator/logger.py` (rotation and `cleanup_old_logs`). Note it executes on import.
- Add API endpoints: modify `src/api/routes.py` and `src/api/app.py` (blueprint `api_blueprint` is registered at `/api`). Ensure PYTHONPATH or editable install so imports resolve.

**Developer checks before PR**
- Run `pytest tests/` and fix regressions; tests currently cover config, selection, packaging, and logging.
- Ensure added files are reachable via imports (prefer `pip install -e .` during development to avoid fiddly PYTHONPATH issues).

**Small gotchas discovered in the code**
- Import side-effects: simply importing `beat_challenge_generator.logger` or `beat_challenge_generator.config` will create files/folders and rotate logs — tests assume this; be careful when writing tests that import these modules.
- API runnable path: the Flask package is under `src/api`. If not installed, set `PYTHONPATH=src` (Windows PowerShell: `$env:PYTHONPATH='src'`) before `python -m api.app`.

If any of these points are unclear or you'd like examples of edits (small PRs for changing selection rules, zip layout, or an extra API route), tell me which area to modify and I will produce a targeted patch and tests.

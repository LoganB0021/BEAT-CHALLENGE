
````markdown
# 🎵 Beat Challenge Generator

A Python-based tool that **randomly selects beat components** (Drum Kits, FX, Samples), packages them into a zip file, and **stores metadata in a database** for reproducible, deterministic beat-making challenges.

## 📌 Features

- **Database-backed selection**: Ingest beats/tree once, then select deterministically from the DB (reproducible challenges).
- **Supports folders**: Drum Kits can be folders; they're preserved in the zip file.
- **Deterministic checksums**: SHA256 checksums for files; nested directory checksums for folders (sorted, deterministic).
- **Dry-run ingest**: Test database population without committing via `--dry-run` flag.
- **Category filtering**: Ingest only specific categories (drum_kits, fx, samples) via `--category` flag.
- **Structured output**: Generated packs stored in `output/packs/`.
- **Comprehensive logging**: All activity logged to `logs/`; rotates at 5 MB, keeps last 5 logs.
- **API support**: Flask endpoints to serve daily challenges and pack metadata.
- **Automated tests**: Covers config, selection, packaging, logging, and ingest.

## 🛠️ Installation & Setup (uv Package Manager)

We now use **[uv](https://docs.astral.sh/uv/concepts/)** for environment and dependency management.

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/your-username/beat-challenge-generator.git
cd beat-challenge-generator
````

### 2️⃣ Create & Activate the uv Virtual Environment

uv automatically creates a project-specific environment:

```sh
uv venv create
```

Activate it:

* **Windows (PowerShell)**:

```sh
.venv\Scripts\Activate.ps1
```

* **Mac/Linux**:

```sh
source .venv/bin/activate
```

> If VS Code prompts to switch Python environments, select the newly created `.venv`.

### 3️⃣ Install Dependencies

```sh
uv sync
```

* Installs all **runtime dependencies** listed in `pyproject.toml`.
* Installs **dev dependencies** (like `pytest`) from `[tool.uv.dependency-groups]`.
* Generates/updates `uv.lock` for reproducibility.

### 4️⃣ Verify Installation

```sh
uv pip list
```

This will show all installed packages inside the uv-managed environment.

---

## 🚀 Running the Application

### Generate a Beat Challenge (CLI)

```sh
uv run python -m beat_challenge_generator.main
```

This will:

* Ensure `beats/`, `output/`, `data/`, and `logs/` directories exist.
* Select one item per category (drum_kits, fx, samples) deterministically from the database.
* Package the selection into a zip file in `output/packs/`.
* Log all details in `logs/`.

### Ingest Beats into the Database

Before selecting, ingest your beats/ directory tree:

```sh
# Ingest all categories
uv run python -m beat_challenge_generator.ingest

# Dry-run: see what would be added without committing
uv run python -m beat_challenge_generator.ingest --dry-run

# Ingest only drum_kits
uv run python -m beat_challenge_generator.ingest --category drum_kits

# Dry-run only fx
uv run python -m beat_challenge_generator.ingest --dry-run --category fx
```

**Ingest details:**

* Walks `beats/` and computes SHA256 checksums for all files and directories.
* Directory checksums are deterministic (sorted by file path, includes nested structure).
* Upserts Sound records into the database (`data/beat_challenge.db` by default).
* Idempotent: only updates records if checksum/size/is_folder changed.
* Use `--dry-run` to preview changes without committing.

### Run the HTTP API (Development)

Ensure `PYTHONPATH` includes `src` and run:

```sh
# Windows PowerShell
$env:PYTHONPATH='src'; uv run python -m api.app

# Mac/Linux
export PYTHONPATH=src && uv run python -m api.app
```

The Flask API starts on `http://localhost:5000/` with endpoints:

* `GET /api/daily-challenge` — returns JSON with selected files and pack metadata.
* Additional endpoints available via `src/api/routes.py`.

---

## 🧪 Running Tests

This project includes **automated tests** using `pytest`.

### Run Tests

```sh
uv run pytest tests/
```

For verbose output:

```sh
uv run pytest -v
```

> `pytest` is installed automatically as a dev dependency in the uv environment.

---

## 📂 Folder Structure

```
beat-challenge-generator/
│── beats/                           # Beat component storage
│   ├── drum_kits/                   # Folders or files (folders preserved in zip)
│   ├── fx/                          # FX files
│   ├── samples/                     # Sample files
│── output/                          # Output artifacts
│   └── packs/                       # Generated beat challenge zips
│── data/                            # Persistent data
│   └── beat_challenge.db            # SQLite database with Sound & Pack records
│── logs/                            # Application logs (rotates, keeps last 5)
│── tests/                           # Automated test files
│   ├── test_config.py
│   ├── test_file_selector.py
│   ├── test_file_manager.py
│   ├── test_logger.py
│   ├── test_ingest.py               # (new)
│   └── __init__.py
│── src/
│   ├── beat_challenge_generator/
│   │   ├── __init__.py
│   │   ├── main.py                  # Entry point
│   │   ├── config.py                # Directories & setup
│   │   ├── logger.py                # Logging configuration
│   │   ├── db.py                    # SQLAlchemy setup & init_db()
│   │   ├── models.py                # Sound & Pack ORM models (new)
│   │── ingest.py                     # Database population from beats/ (new)
│   │── file_selector.py              # Selects beats (now queries DB)
│   │── file_manager.py               # Zips selected files
│   └── api/
│       ├── app.py                    # Flask app
│       └── routes.py                 # API endpoints
│── pyproject.toml                   # Dependencies & package config
│── README.md                        # This file
└── .gitignore
```

---

## 🆕 Database & Models

### Architecture

The project now uses **SQLAlchemy ORM** with a SQLite database (configurable via `DATABASE_URL` environment variable).

**Models:**

* `Sound`: represents a file or folder in beats/

  * Fields: `id`, `category` (drum_kits|fx|samples), `filename`, `checksum`, `size`, `is_folder`, `items` (JSON for tags/metadata)
* `Pack`: represents a generated challenge

  * Fields: `id`, `created_at`, `items` (JSON list of selected Sound IDs)

### Environment Variables

* `DATABASE_URL` (optional): SQLAlchemy DSN. Defaults to `sqlite:///data/beat_challenge.db`.
  Example for Postgres: `DATABASE_URL=postgresql://user:pass@localhost/beat_challenge`

---

## 🛠️ Making Your Own Modifications

### Adding New Sounds

Place files or folders inside:

```
beats/drum_kits/        # Can contain files or subdirectories
beats/fx/
beats/samples/
```

Then ingest:

```sh
uv run python -m beat_challenge_generator.ingest
```

### Customizing Selection Logic

Edit `src/beat_challenge_generator/file_selector.py`.

### Customizing Pack Structure

Edit `src/beat_challenge_generator/file_manager.py`.

### Changing Logging Behavior

Edit `src/beat_challenge_generator/logger.py`.

### Adding API Endpoints

Modify `src/api/routes.py` and register new endpoints in `src/api/app.py`.

---

## 🐛 Troubleshooting

| Problem                | Solution                                                                         |
| ---------------------- | -------------------------------------------------------------------------------- |
| `ModuleNotFoundError`  | Run `uv sync` inside the uv environment.                                         |
| `No such table: sound` | Run `uv run python -m beat_challenge_generator.ingest` to populate the database. |
| `DATABASE_URL` errors  | Ensure `DATABASE_URL` is a valid SQLAlchemy DSN (defaults to SQLite in `data/`). |
| Logs not appearing     | Check `logs/` folder or verify `logger.py` config.                               |
| Tests failing          | Run `uv run pytest -v tests/` to see which test failed and why.                  |
| API won't start        | Ensure `PYTHONPATH=src` is set before running `uv run python -m api.app`.        |

---

## 📋 Recommended Next Steps

1. Wire deterministic selection: Update `file_selector.py` to prioritize DB queries with intelligent filtering.
2. Extend pack creation: Update `file_manager.py` and `main.py` to create Pack records and store pack metadata.
3. Add pack replay: Implement an endpoint to reconstruct a past challenge from a Pack record's Sound IDs and checksums.
4. Add tagging: Extend the Sound model with tags (drum_kit="boom", "analog", etc.) and filter by tags during selection.

---

## 📜 License

MIT License

## ✨ Contributors

* **[Your Name]** - Initial development
* AI Assistant — Database integration, ingest pipeline, and deterministic selection

## 🎵 Have Fun Making Beats

🚀🔥 For official uv documentation, see: [https://docs.astral.sh/uv/concepts/](https://docs.astral.sh/uv/concepts/)

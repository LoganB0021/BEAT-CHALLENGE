# 🎵 Beat Challenge Generator

A Python-based tool that **randomly selects beat components** (Drum Kits, FX, Samples), packages them into a zip file, and **stores metadata in a database** for reproducible beat-making challenges.

---

## 📌 Features

* **Database-backed selection**: Deterministic selection of beats from the database.
* **Supports folders**: Drum Kits can be folders; preserved in the zip file.
* **Deterministic checksums**: SHA256 checksums for files; nested directory checksums for folders.
* **Dry-run ingest**: Test database population without committing via `--dry-run`.
* **Category filtering**: Ingest specific categories via `--category`.
* **Structured output**: Generated packs stored in `output/packs/`.
* **Comprehensive logging**: Logs in `logs/`, rotates at 5 MB, keeps last 5 logs.
* **API support**: Flask endpoints to serve daily challenges and pack metadata.
* **Automated tests**: Covers config, selection, packaging, logging, and ingest.

---

## ⚡ Quickstart (New Machine / Dev Setup)

This is the fastest way to get started:

```powershell
# Clone repo and enter
git clone https://github.com/your-username/beat-challenge-generator.git
cd beat-challenge-generator

# Create virtual environment and activate
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows PowerShell
# source .venv/bin/activate    # Mac/Linux

# Install uv package manager and sync dependencies
pip install uv
uv sync

# Initialize local DB and populate with demo data
uv run python scripts/db_demo.py
```

After this, you have a working local DB with demo data, and you can immediately run the generator or API.

---

## 🚀 Running the Application

### Generate a Beat Challenge (CLI)

```sh
uv run beat-gen
```

* Selects one item per category (drum_kits, fx, samples).
* Packages selection into a zip in `output/packs/`.
* Logs all activity in `logs/`.

---

### Initialize Local Demo Database

If you haven’t run it during Quickstart:

```sh
uv run python scripts/db_demo.py
```

* Creates SQLite DB tables if they don’t exist.
* Inserts a sample `Sound` record (`drum_kits/demo_kick.wav`).
* Creates a demo `Pack` record for today.
* Prints resolved paths for verification.

---

### Ingest Beats into the Database

Use the **ingest entry point** for your real beats:

```sh
# Ingest all categories
uv run ingest

# Dry-run: preview changes without committing
uv run ingest --dry-run

# Ingest only drum_kits
uv run ingest --category drum_kits
```

* Computes SHA256 checksums for files/folders.
* Upserts `Sound` records into `data/beat_challenge.db`.
* `--dry-run` previews changes without committing.

---

## 🧪 Running Tests

```sh
uv run pytest tests/
uv run pytest -v tests/
```

---

## 📂 Folder Structure

```
beat-challenge-generator/
│── beats/
│   ├── drum_kits/
│   ├── fx/
│   └── samples/
│── output/
│   └── packs/
│── data/
│   └── beat_challenge.db
│── logs/
│── scripts/
│   └── db_demo.py
│── tests/
│── src/
│   ├── beat_challenge_generator/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── ingest.py
│   │   ├── file_selector.py
│   │   └── file_manager.py
│   └── api/
│       ├── app.py
│       └── routes.py
│── pyproject.toml
│── README.md
└── .gitignore
```

---

## 🐛 Troubleshooting

| Problem                | Solution                                                   |
| ---------------------- | ---------------------------------------------------------- |
| `ModuleNotFoundError`  | Run `uv sync` inside the venv.                             |
| `No such table: sound` | Run `uv run ingest` or `uv run python scripts/db_demo.py`. |
| Tests failing          | Run `uv run pytest -v tests/`.                             |

---

## ✨ Contributors

* **[Your Name]** — Initial development
* AI Assistant — Database integration, ingest pipeline, and deterministic selection
Perfect! Here’s a **fully updated, simplified README** for your Beat Challenge Generator project, using standard Python venvs and the proper `uv run` entry points for both `beat-gen` and `ingest`.

---

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

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/your-username/beat-challenge-generator.git
cd beat-challenge-generator
```

### 2️⃣ Create & Activate a Python Virtual Environment

```sh
python -m venv .venv
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

---

### 3️⃣ Install `uv` and Sync Dependencies

```sh
pip install uv
uv sync
```

* Installs all dependencies listed in `pyproject.toml`.
* Generates/updates `uv.lock` for reproducibility.

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

### Ingest Beats into the Database

Use the **ingest entry point**:

```sh
# Ingest all categories
uv run ingest

# Dry-run: preview changes without committing
uv run ingest --dry-run

# Ingest only drum_kits
uv run ingest --category drum_kits
```

* Computes SHA256 checksums for files/folders.
* Upserts Sound records into the database (`data/beat_challenge.db`).
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

| Problem                | Solution                       |
| ---------------------- | ------------------------------ |
| `ModuleNotFoundError`  | Run `uv sync` inside the venv. |
| `No such table: sound` | Run `uv run ingest`.           |
| Tests failing          | Run `uv run pytest -v tests/`. |

---

## ✨ Contributors

* **[Your Name]** — Initial development
* AI Assistant — Database integration and ingest pipeline

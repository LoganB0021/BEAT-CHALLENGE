# 🎵 Beat Challenge Generator

A Python-based tool that **randomly selects beat components** (Drum Kits, FX, Melodies) and packages them into a zip file for beat-making challenges.

## 📌 Features

- Randomly selects **drum kits (folders), FX, and melodies**.
- **Supports folders** (Drum Kits) and ensures they are correctly added to the zip file.
- Organizes files into **a structured output folder**.
- **Logs all activity** to track selected files, errors, and system info.
- **Automatically cleans up old log files** (only keeps the last 5).
- **Includes automated tests** to verify functionality.

## 🛠️ Installation & Setup

### 1️⃣ **Clone the Repository**

```sh
git clone https://github.com/your-username/beat-challenge-generator.git
cd beat-challenge-generator
```

### 2️⃣ **Create a Virtual Environment**

```sh
python -m venv venv
```

### 3️⃣ **Activate the Virtual Environment**

- **Windows**:

  ```sh
  venv\Scripts\activate
  ```

- **Mac/Linux**:

  ```sh
  source venv/bin/activate
  ```

### 4️⃣ **Install Dependencies**

```sh
pip install -e .
```

## 🚀 Running the Application

After setting up the environment, run:

```sh
python -m beat_challenge_generator.main
```

Upon running, the program will:

- Ensure **`beats/`**, **`output/`**, and **`logs/`** directories exist.
- Randomly select a drum kit (folder or file), an FX sample, and a melody.
- Package the selection into a zip file inside `output/`.
- Log all details in `logs/`.

## 🧪 Running Tests

This project includes **automated tests** using `pytest`.  

### **1️⃣ Install `pytest`**

If you haven't installed `pytest`, run:

```sh
pip install pytest
```

### **2️⃣ Run All Tests**

From the project root, run:

```sh
pytest tests/
```

For more detailed output:

```sh
pytest -v
```

### **3️⃣ What’s Being Tested?**

| Test File | What It Tests |
|-----------|--------------|
| `test_config.py` | Ensures required directories (`beats/`, `output/`, `logs/`) are created. |
| `test_file_selector.py` | Ensures random selection of files and folders works correctly. |
| `test_file_manager.py` | Ensures selected files and folders are properly added to a zip. |
| `test_logger.py` | Ensures logs are created when the application runs. |

### **4️⃣ Pre-commit Testing**

To automatically run tests before each commit:

1. Add a **pre-commit hook**:

   ```sh
   echo "pytest tests/" > .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit
   ```

2. Now, every time you commit changes:

   ```sh
   git commit -m "Your commit message"
   ```

   The tests will run first! If any test **fails**, the commit will be blocked.

## 📂 Folder Structure

```
beat-challenge-generator/
│── beats/                 # Beat component storage (Drum Kits, FX, Melodies)
│   ├── Drum Kits/
│   ├── FX/
│   ├── Melodies/
│── output/                # Stores generated beat zip files
│── logs/                  # Stores application logs (only last 5 kept)
│── tests/                 # Contains automated test files
│   ├── test_config.py
│   ├── test_file_selector.py
│   ├── test_file_manager.py
│   ├── test_logger.py
│   ├── __init__.py
│── src/
│   ├── beat_challenge_generator/
│   │   ├── __init__.py
│   │   ├── main.py        # Entry point of the application
│   │   ├── config.py      # Manages directories & setup
│   │   ├── logger.py      # Handles logging
│   │   ├── file_selector.py  # Selects random beats
│   │   ├── file_manager.py   # Zips selected files
│── pyproject.toml         # Manages dependencies
│── README.md              # This file!
│── .gitignore             # Prevents unnecessary files from being committed
```

## 🛠️ Making Your Own Modifications

### ✅ **Adding New Sounds**

Place your own sound files inside:

```
beats/Drum Kits/
beats/FX/
beats/Melodies/
```

Folders inside `Drum Kits/` are supported!

### ✅ **Customizing Beat Selection**

Modify **`file_selector.py`** if you want to change how beats are chosen.

### ✅ **Customizing Zip File Creation**

Modify **`file_manager.py`** to change how files are organized inside the zip.

### ✅ **Changing Logging Behavior**

Modify **`logger.py`** to adjust log retention, file rotation, or verbosity.

## 🐛 Troubleshooting

| Problem | Solution |
|---------|---------|
| `ModuleNotFoundError` | Run `pip install -e .` inside the virtual environment. |
| No files found | Ensure `beats/` contains `.wav` files or folders inside `Drum Kits/`. |
| Logs not appearing | Check `logs/` folder or update `logger.py` to debug. |
| Tests failing | Run `pytest -v tests/` and check which test is failing. |

## 📜 License

MIT License

## ✨ Contributors

- **[Your Name]** - Initial development

## 🎵 Have Fun Making Beats

🚀🔥 Let me know if you need more info! 🎧🎼

```

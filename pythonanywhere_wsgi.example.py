"""Example PythonAnywhere WSGI configuration.

Copy the relevant contents into the WSGI file shown in PythonAnywhere's Web
tab and replace USERNAME with the account name.
"""

import os
import sys
from pathlib import Path

PROJECT_HOME = "/home/USERNAME/BEAT-CHALLENGE"
SRC_HOME = os.path.join(PROJECT_HOME, "src")

if SRC_HOME not in sys.path:
    sys.path.insert(0, SRC_HOME)

os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{PROJECT_HOME}/data/beat_challenge.db",
)
SECRET_KEY_FILE = Path("/home/USERNAME/.config/beat-challenge/secret_key")
if not SECRET_KEY_FILE.is_file():
    raise RuntimeError(f"Missing secret key file: {SECRET_KEY_FILE}")
os.environ["SECRET_KEY"] = SECRET_KEY_FILE.read_text(encoding="utf-8").strip()
if not os.environ["SECRET_KEY"]:
    raise RuntimeError(f"Secret key file is empty: {SECRET_KEY_FILE}")
os.environ.setdefault("ALLOW_RANDOM_CHALLENGES", "false")
os.environ.setdefault("ALLOW_ASYNC_CHALLENGES", "false")
# Set this only when random generation is enabled and the endpoint is protected.
# os.environ.setdefault("BEAT_API_KEY", "set-this-outside-source-control")
# os.environ.setdefault("TRUSTED_HOSTS", "USERNAME.pythonanywhere.com")

from api.app import app as application  # noqa: F401

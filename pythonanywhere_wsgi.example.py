"""Example PythonAnywhere WSGI configuration.

Copy the relevant contents into the WSGI file shown in PythonAnywhere's Web
tab and replace USERNAME with the account name.
"""

import os
import sys

PROJECT_HOME = "/home/USERNAME/BEAT-CHALLENGE"
SRC_HOME = os.path.join(PROJECT_HOME, "src")

if SRC_HOME not in sys.path:
    sys.path.insert(0, SRC_HOME)

os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{PROJECT_HOME}/data/beat_challenge.db",
)
os.environ.setdefault("SECRET_KEY", "set-this-in-pythonanywhere")
os.environ.setdefault("ALLOW_RANDOM_CHALLENGES", "false")
os.environ.setdefault("ALLOW_ASYNC_CHALLENGES", "false")
# Set this only when random generation is enabled and the endpoint is protected.
# os.environ.setdefault("BEAT_API_KEY", "set-this-outside-source-control")
# os.environ.setdefault("TRUSTED_HOSTS", "USERNAME.pythonanywhere.com")

from api.app import app as application

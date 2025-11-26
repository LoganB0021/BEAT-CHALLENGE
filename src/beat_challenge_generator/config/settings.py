import os
from beat_challenge_generator.config.paths import DATA_DIR

# Default SQLite database
_default_db_path = os.path.join(DATA_DIR, "beat_challenge.db")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{_default_db_path}"
)

# Future:
# SECRET_KEY = os.getenv("SECRET_KEY", "local-dev-key")
# ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

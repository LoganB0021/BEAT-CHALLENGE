import datetime
import glob
from loguru import logger
import os

# Base directory (the root of the project)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Logs directory
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Make sure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Generate a unique log file name based on the current timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"app_{timestamp}.log")

# Add a log file, rotating at 5 MB and keeping the last 5 logs
logger.add(LOG_FILE, rotation="5 MB", level="INFO")

def cleanup_old_logs(log_dir, keep=5):
    """Keeps only the last `keep` log files and deletes older ones."""
    log_files = sorted(glob.glob(os.path.join(log_dir, "app_*.log")), reverse=True)

    if len(log_files) > keep:
        for old_log in log_files[keep:]:
            try:
                os.remove(old_log)
                logger.info(f"Deleted old log file: {old_log}")
            except Exception as e:
                logger.error(f"Failed to delete log file {old_log}: {e}")

# Cleanup logs before continuing
cleanup_old_logs(LOG_DIR)

# Initial log to confirm the logger is set up
logger.info("Logger initialized!")

# Meta Data
logger.info(f"BASE_DIR is set to: {BASE_DIR}")
logger.info(f"📂 Log File Path: {LOG_DIR}")

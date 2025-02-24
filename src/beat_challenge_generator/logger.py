import datetime
from loguru import logger
import os
from beat_challenge_generator.config import LOG_DIR, BASE_DIR

# Make sure the logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Generate a unique log file name based on the current timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"app_{timestamp}.log")

# Add a log file, rotating at 5 MB and keeping the last 5 logs
logger.add(LOG_FILE, rotation="5 MB", retention=5, level="INFO")

# Initial log to confirm the logger is set up
logger.info("Logger initialized!")

# Meta Data
logger.info(f"BASE_DIR is set to: {BASE_DIR}")
logger.info(f"📂 Log File Path: {LOG_DIR}")

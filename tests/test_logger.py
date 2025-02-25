import os
import datetime
from beat_challenge_generator.logger import LOG_DIR, logger

def test_log_file_creation():
    """Ensure a log file is created when logger is used."""
    
    # Ensure the log directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    # Generate a temporary test log filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    test_log_file = os.path.join(LOG_DIR, f"test_log_{timestamp}.log")

    # Capture initial log files
    log_files_before = set(os.listdir(LOG_DIR))

    # Add a temporary log file sink
    logger.add(test_log_file, level="INFO")

    # Write a log message and flush it
    logger.info("Testing log creation")
    logger.complete()  # Flush log messages immediately

    # Capture new log files
    log_files_after = set(os.listdir(LOG_DIR))

    # Remove test log sink to clean up
    logger.remove()

    # Identify new log files
    new_logs = log_files_after - log_files_before

    assert len(new_logs) > 0, "No new log file was created."

    # Cleanup test log file
    for log in new_logs:
        os.remove(os.path.join(LOG_DIR, log))

import logging
import os
import sys

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Create logger
logger = logging.getLogger("datachat")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers if re-imported
if not logger.handlers:
    # Formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(os.path.join(LOG_DIR, "datachat.log"))
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.stream = open(sys.stdout.fileno(), 
        mode='w', 
        encoding='utf-8', 
        buffering=1)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_question(question: str):
    """Logs the user question."""
    logger.info(f"Question: {question}")


def log_sql(sql: str):
    """Logs the generated SQL."""
    logger.info(f"SQL: {sql}")


def log_execution_time(operation: str, seconds: float):
    """Logs execution time for an operation."""
    logger.info(f"{operation} took {seconds:.4f} seconds")


def log_error(error: str):
    """Logs an error message."""
    logger.error(f"Error: {error}")


def log_result_count(count: int):
    """Logs the number of rows returned."""
    logger.info(f"Rows returned: {count}")
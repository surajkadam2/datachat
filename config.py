# =========================
# AI CONFIGURATION
# Controls model behavior for SQL generation and explanations
# =========================
GEMINI_MODEL = "gemini-2.5-flash"
TEMPERATURE_SQL = 0.0
TEMPERATURE_EXPLAIN = 0.1
MAX_TOKENS = 500


# =========================
# DATABASE CONFIGURATION
# Controls query execution limits and schema caching
# =========================
QUERY_TIMEOUT_SECONDS = 10
MAX_ROWS_RETURNED = 100
SCHEMA_CACHE_TTL_HOURS = None  # Not implemented yet, placeholder


# =========================
# SAFETY CONFIGURATION
# Controls blocked keywords for user input and SQL queries
# =========================
DANGEROUS_INPUT_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "EXEC"
]

DANGEROUS_SQL_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER", "EXEC"
]


# =========================
# EXPLAINER CONFIGURATION
# Controls how much data and length is used for explanations
# =========================
MAX_ROWS_TO_EXPLAINER = 20
MAX_EXPLANATION_SENTENCES = 3


# =========================
# MEMORY CONFIGURATION
# Controls conversation memory behavior
# =========================
MAX_HISTORY_ITEMS = 5


# =========================
# UI CONFIGURATION
# Controls CLI display settings
# =========================
APP_NAME = "DataChat CLI"
APP_VERSION = "1.0"
CLI_PROMPT = "You"
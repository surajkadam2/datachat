import time
from claude import ask_claude
from safety import extract_sql, is_sql_safe
from logger import log_question, log_execution_time, logger
from config import TEMPERATURE_SQL, MAX_HISTORY_ITEMS

# Schema cache
_schema_cache = None


def get_cached_schema(get_schema_fn):
    """
    Retrieves the database schema, using a cache to avoid redundant database calls.
    
    This function implements a simple caching mechanism to avoid querying the database
    schema repeatedly during a session. The schema is fetched on first call and reused
    for subsequent calls.
    
    Args:
        get_schema_fn: A callable that retrieves the database schema when invoked.
            Expected to return a string representation of the schema.
        
    Returns:
        str: The database schema as a string.
        
    Raises:
        Exception: Any exception raised by get_schema_fn will propagate up.
    """
    global _schema_cache

    # Cache on first access to minimize database connections
    if _schema_cache is None:
        _schema_cache = get_schema_fn()

    return _schema_cache


def build_system_prompt(schema: str) -> str:
    """
    Builds the system prompt for Claude to generate SQL queries.
    
    Constructs a prompt that instructs Claude to act as a SQL Server expert with
    strict rules about query generation, safety constraints, and output formatting.
    The schema is embedded to provide table and column context.
    
    Args:
        schema (str): The database schema containing table and column definitions.
        
    Returns:
        str: A formatted system prompt for Claude.
    """
    return f"""
    You are a SQL Server expert.

    Here is the database schema:
    {schema}

    Rules:
    - Return ONLY a valid SQL query
    - Do NOT include explanations
    - Do NOT use markdown or code blocks
    - NEVER use DELETE, DROP, UPDATE, INSERT, TRUNCATE, ALTER, EXEC
    - Use TOP instead of LIMIT
    - Ensure SQL Server syntax only
    - Important : Dont not generatate SQL without Column names or blank name always specify columns explicitly
    - For customer queries select only: CustomerID, CompanyName, 
        ContactName, City, Country unless user asks for more details
    - Never select address, phone, fax, postal code unless explicitly asked
    """


def build_system_prompt_strict(schema: str) -> str:
    """
    Builds the system prompt for Claude with stricter SQL generation rules.
    
    Extends the base system prompt with additional constraints to ensure safer and
    more predictable SQL generation, including row limits, column restrictions, and
    handling of ambiguous queries.
    
    Args:
        schema (str): The database schema containing table and column definitions.
        
    Returns:
        str: A formatted system prompt with strict SQL rules for Claude.
    """
    return f"""
    You are a SQL Server expert.

    Here is the database schema:
    {schema}

    Rules:
    - Return ONLY a valid SQL query
    - Do NOT include explanations
    - Do NOT use markdown or code blocks
    - NEVER use SELECT *
    - ALWAYS select specific columns
    - ALWAYS use TOP 100 maximum
    - Use TOP instead of LIMIT
    - NEVER use DELETE, DROP, UPDATE, INSERT, TRUNCATE, ALTER, EXEC
    - Ensure SQL Server syntax only
    - Ensure for count queries, you return a single column named 'count'
    - Never select more than 5 columns unless user specifically asks for all columns
    - For date columns always use CAST(column AS DATE) to remove time portion
    - When user says 'best', 'top', 'most' without a number, default to TOP 10
    - When question uses words like 'best', 'top', 'most', 'worst', 'least' without specifying a number, always default to TOP 10
    - When question is too vague or doesn't relate to the database, respond with exactly: NOT_A_DB_QUESTION
    - ALWAYS use TOP 10 as default limit unless user specifies a number
    - NEVER return more than 10 rows unless user explicitly asks for more
    - If input contains gibberish mixed with a valid question, extract the valid question and respond with:
        EXTRACTED: <extracted question>
        SQL: <your sql here>
    - If no valid database question found, respond with: NOT_A_DB_QUESTION
    - When user uses references like 'their', 'those', 'them', 'same', 'these' — maintain ALL filters, conditions, and TOP N limits from the previous SQL exactly as they were. Do not broaden the scope.
    """

def build_full_prompt(question: str, schema: str, history: None) -> str:
    """
    Builds the complete prompt for Claude including system instructions and conversation context.
    
    Combines the system prompt, recent conversation history, and the current user question
    into a single prompt. History is truncated to maintain token efficiency and prevent
    Claude from relying too heavily on old context.
    
    Args:
        question (str): The current user's natural language question.
        schema (str): The database schema for context.
        history (list, optional): List of previous question-SQL pairs. Defaults to empty list.
            Each item should have 'question' and 'sql' keys.
        
    Returns:
        str: The complete formatted prompt ready to send to Claude.
    """
    if history is None:
        history = []

    system_prompt = build_system_prompt(schema)

    # Limit history to recent N items to avoid excessive context and token usage
    history = history[- MAX_HISTORY_ITEMS:] if history else []

    history_block = ""
    if history:
        history_block = "Previous conversation:\n"
        for item in history:
            # Include both question and SQL so Claude understands the pattern
            history_block += f"Q: {item['question']}\nSQL: {item['sql']}\n\n"

    return f"""
    {system_prompt}

    {history_block}

    User question:
    {question}
    """

def ask_data_question(question: str, schema: str, history: list = None) -> dict:
    """
    Sends a natural language question to Claude and generates a corresponding SQL query.
    
    This function orchestrates the entire flow of converting a user's natural language
    question into a safe, executable SQL query. It includes built-in safety checks and
    performance monitoring. Any exception that occurs is caught and returned in the
    error field to ensure graceful degradation.

    Args:
        question (str): The user's natural language question about the database.
        schema (str): The database schema providing context for SQL generation.
        history (list, optional): Previous question-SQL pairs for conversational context.
            Each item should have 'question' and 'sql' keys. Defaults to None.
      
    Returns:
        dict: A result dictionary containing:
            - success (bool): Whether a valid and safe SQL query was generated.
            - sql (str or None): The extracted SQL query, or None if generation or
              validation failed.
            - error (str or None): Error message if something went wrong, None on success.
            - gemini_time (float): Time taken for Claude to generate a response in seconds.
        
    Raises:
        No exceptions are raised; all errors are caught and returned in the result dict.
    """
    # Initialize history if not provided to ensure consistent handling
    if history is None:
        history = []

    # Record start time for performance monitoring
    start_time = time.time()

    try:
        # Build prompt with system instructions, context history, and current question
        full_prompt = build_full_prompt(question, schema, history)
        # Send to Claude and get raw response text
        raw_response = ask_claude(full_prompt, temperature=TEMPERATURE_SQL)

        # Calculate elapsed time for logging and performance analysis
        gemini_time = time.time() - start_time
        log_execution_time("Gemini response", gemini_time)

        # Extract SQL from response; Claude may include explanation text we need to filter
        sql = extract_sql(raw_response)

        # No SQL extraction means question was out of scope or response was invalid
        if not sql:
            return {
                "success": False,
                "sql": None,
                "error": "No SQL generated",
                "gemini_time": gemini_time
            }

        # Validate SQL safety before allowing execution (prevents injection/destructive queries)
        if not is_sql_safe(sql):
            return {
                "success": False,
                "sql": sql,
                "error": "Unsafe SQL detected",
                "gemini_time": gemini_time
            }

        # All validation passed; return successful result with generated SQL
        return {
            "success": True,
            "sql": sql,
            "error": None,
            "gemini_time": gemini_time
        }

    except Exception as e:
        # Catch any unexpected errors and return them gracefully in result dict
        gemini_time = time.time() - start_time
        return {
            "success": False,
            "sql": None,
            "error": str(e),
            "gemini_time": gemini_time
        }


if __name__ == "__main__":
    from db import get_schema

    schema = get_cached_schema(get_schema)

    result = ask_data_question(
        "Show me top 5 orders with customer company names and order dates",
        schema
    )

        # Access result correctly
    logger.info(f"Success: {result['success']}")
    logger.info(f"SQL: {result['sql']}")
    logger.info(f"Gemini time: {result['gemini_time']} seconds")
import time
from claude import ask_claude
from safety import extract_sql, is_sql_safe
from logger import log_question, log_execution_time, logger

# Schema cache
_schema_cache = None


def get_cached_schema(get_schema_fn):
    """
    Returns cached schema if available, otherwise fetches and caches it.
    """
    global _schema_cache

    if _schema_cache is None:
        _schema_cache = get_schema_fn()

    return _schema_cache


def build_system_prompt(schema: str) -> str:
    """
    Builds system prompt for Gemini.
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
    """


def build_system_prompt(schema: str) -> str:
    """
    Builds system prompt for Gemini with stricter SQL rules.
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
    - For date columns always use CAST(column AS DATE) to remove time portio
    - When user says 'best', 'top', 'most' without a number, default to TOP 10
    - When question uses words like 'best', 'top', 'most', 'worst', 'least' without specifying a number,  always default to TOP 10
    - When question is too vague or doesn't relate to the database, respond with exactly: NOT_A_DB_QUESTION
    - ALWAYS use TOP 10 as default limit unless user specifies a number
    - NEVER return more than 10 rows unless user explicitly asks for more
    -  If input contains gibberish mixed with a valid question, 
        extract the valid question and respond with:
        EXTRACTED: <extracted question>
        SQL: <your sql here>
    - If no valid database question found, respond with: NOT_A_DB_QUESTION
    """


def ask_data_question(question: str, schema: str) -> dict:
    """
    Sends question to Gemini, extracts SQL, validates safety,
    and logs execution time.
    """
    start_time = time.time()

    try:
        #log_question(question)

        system_prompt = build_system_prompt(schema)

        full_prompt = f"""
        {system_prompt}

        User question:
        {question}
        """

        raw_response = ask_claude(full_prompt)

        gemini_time = time.time() - start_time
        log_execution_time("Gemini response", gemini_time)

        sql = extract_sql(raw_response)

        if not sql:
            return {
                "success": False,
                "sql": None,
                "error": "No SQL generated",
                "gemini_time": gemini_time
            }

        if not is_sql_safe(sql):
            return {
                "success": False,
                "sql": sql,
                "error": "Unsafe SQL detected",
                "gemini_time": gemini_time
            }

        return {
            "success": True,
            "sql": sql,
            "error": None,
            "gemini_time": gemini_time
        }

    except Exception as e:
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
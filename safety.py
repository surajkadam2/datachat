import re
from config import DANGEROUS_INPUT_KEYWORDS, DANGEROUS_SQL_KEYWORDS

def is_input_safe(user_input: str) -> bool:
    """
    Checks if user input contains dangerous SQL keywords.
    Returns False if found, True if safe.
    """
    upper_input = user_input.upper()
    return not any(keyword in upper_input for keyword in DANGEROUS_INPUT_KEYWORDS)


def is_sql_safe(sql: str) -> bool:
    """
    Checks if generated SQL contains dangerous keywords.
    Returns False if found, True if safe.
    """
    upper_sql = sql.upper()
    return not any(keyword in upper_sql for keyword in DANGEROUS_SQL_KEYWORDS)


def extract_sql(raw_response: str) -> str:
    """
    Extracts clean SQL from Gemini response by removing markdown code blocks.
    """
    # Remove ```sql ... ``` or ``` ... ```
    cleaned = re.sub(r"```sql\s*([\s\S]*?)```", r"\1", raw_response, flags=re.IGNORECASE)
    cleaned = re.sub(r"```\s*([\s\S]*?)```", r"\1", cleaned)

    # Strip leading/trailing whitespace
    return cleaned.strip()


if __name__ == "__main__":
    # Test cases
    tests = []

    # Test is_input_safe
    tests.append(("Input Safe", is_input_safe("Show all users") == True))
    tests.append(("Input Unsafe", is_input_safe("DROP TABLE users") == False))

    # Test is_sql_safe
    tests.append(("SQL Safe", is_sql_safe("SELECT * FROM users") == True))
    tests.append(("SQL Unsafe", is_sql_safe("DELETE FROM users") == False))

    # Test extract_sql
    raw = "```sql\nSELECT * FROM users;\n```"
    extracted = extract_sql(raw)
    tests.append(("Extract SQL", extracted == "SELECT * FROM users;"))

    # Print results
    for name, result in tests:
        print(f"{name}: {'PASS' if result else 'FAIL'}")
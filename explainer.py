import time
from claude import ask_claude
from logger import log_execution_time


def explain_results(question: str, rows: list, sql: str) -> str:
    """
    Generates a natural language explanation of query results.
    """
    start_time = time.time()

    # Limit rows to first 20
    limited_rows = rows[:20] if rows else []

    # Format rows as simple list
    rows_text = ""
    if not limited_rows:
        rows_text = "[]"
    else:
        rows_text = "\n".join([str(row) for row in limited_rows])

    # Build prompt
    prompt = f"""
You are a data analyst.

System rules:
- Answer in 2-3 sentences maximum
- Use ONLY the provided data
- Always include exact numbers
- Never invent facts
- If data is empty say: "No results found"
- Express uncertainty with: "Based on available data"

Original Question:
{question}

SQL Query:
{sql}

Data:
{rows_text}

Provide a clear answer:
"""

    response = ask_claude(prompt)

    execution_time = time.time() - start_time
    log_execution_time("Explanation generation", execution_time)

    return response.strip()


if __name__ == "__main__":
    sample_rows = [
        {"CompanyName": "Alfreds Futterkiste", "Country": "Germany"},
        {"CompanyName": "Blauer See Delikatessen", "Country": "Germany"},
        {"CompanyName": "Drachenblut Delikatessen", "Country": "Germany"},
    ]
    
    result = explain_results(
        question="Show me customers from Germany",
        rows=sample_rows,
        sql="SELECT CompanyName, Country FROM Customers WHERE Country = 'Germany'"
    )
    print("Explanation:\n", result)
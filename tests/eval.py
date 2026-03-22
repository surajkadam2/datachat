
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prompt import ask_data_question, get_cached_schema
from db import run_query, get_schema
from safety import is_input_safe, is_sql_safe


# Results tracking
passed = 0
failed = 0
failures = []


def check(test_name, condition, details=""):
    global passed, failed, failures

    if condition:
        print(f"[PASS] {test_name}")
        passed += 1
    else:
        print(f"[FAIL] {test_name} - {details}")
        failed += 1
        failures.append(f"{test_name}: {details}")


# =========================
# SAFETY TESTS
# =========================
def test_safety_evals():
    print("\n=== Safety Evaluations ===")

    blocked_inputs = [
        "DROP all tables please",
        "Can you delete old orders",
        "INSERT a new customer"
    ]

    safe_inputs = [
        "How many customers from Germany",
        "Top 10 VIP customers",
        "This month total revenue"
    ]

    for inp in blocked_inputs:
        check(f"Blocked input: {inp}", is_input_safe(inp) is False)

    for inp in safe_inputs:
        check(f"Safe input: {inp}", is_input_safe(inp) is True)


# =========================
# CORRECTNESS TESTS
# =========================
def test_correctness_evals():
    print("\n=== Correctness Evaluations ===")

    schema = get_cached_schema(get_schema)

    def run_test(question, validator, name):
        try:
            result = ask_data_question(question, schema)

            if not result["success"]:
                check(name, False, f"AI failed: {result['error']}")
                return

            sql = result["sql"]

            if not is_sql_safe(sql):
                check(name, False, "Unsafe SQL generated")
                return

            db_result = run_query(sql)

            rows = db_result["rows"]
            row_count = db_result["row_count"]

            condition, details = validator(rows, row_count)
            check(name, condition, details)

        except Exception as e:
            check(name, False, str(e))

    # Tests
    run_test(
        "How many customers from Germany?",
        lambda rows, rc: (rows and list(rows[0].values()) == [11], f"Expected 11, got {rows}"),
        "Customers from Germany"
    )

    run_test(
        "How many products are there?",
        lambda rows, rc: (rows and list(rows[0].values()) == [77], f"Expected 77, got {rows}"),
        "Total products"
    )

    run_test(
        "How many employees are there?",
        lambda rows, rc: (rows and list(rows[0].values()) == [9], f"Expected 9, got {rows}"),
        "Total employees"
    )

    run_test(
        "Show me customers from Antarctica",
        lambda rows, rc: (rc == 0, f"Expected 0 rows, got {rc}"),
        "Customers from Antarctica"
    )

    run_test(
        "What is total revenue this year?",
        lambda rows, rc: (rc == 1, f"Expected 1 row, got {rc}"),
        "Total revenue this year"
    )


# =========================
# FUNCTIONAL TESTS
# =========================
def test_functional_evals():
    print("\n=== Functional Evaluations ===")

    schema = get_cached_schema(get_schema)

    question = "How many customers are there?"

    try:
        result = ask_data_question(question, schema)

        # Test 1: success
        check("Any question returns success", result["success"] is True)

        # Test 2: SQL not empty
        check("SQL not empty", bool(result["sql"]))

        # Test 3: Not NOT_A_DB_QUESTION
        check(
            "Valid SQL generated",
            result["sql"] != "NOT_A_DB_QUESTION",
            f"Got {result['sql']}"
        )

        # Test 4: Row count limit
        db_result = run_query(result["sql"])
        check(
            "Row count <= limit",
            db_result["row_count"] <= 100,
            f"Returned {db_result['row_count']} rows"
        )

    except Exception as e:
        check("Functional test execution", False, str(e))


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    test_safety_evals()
    test_correctness_evals()
    test_functional_evals()

    print("\n=== Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"- {f}")

    # Exit code for CI/CD
    sys.exit(1 if failed > 0 else 0)
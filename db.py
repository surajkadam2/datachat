import os
import time
import warnings

from dotenv import load_dotenv
from sqlalchemy import create_engine, text,exc,inspect
from logger import log_sql, log_execution_time, log_error, logger

warnings.filterwarnings("ignore", category=exc.SAWarning)

# Load environment variables
load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")

# Create connection string
connection_string = (
    f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}"
    "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

# Create SQLAlchemy engine
engine = create_engine(connection_string)


from sqlalchemy import inspect

def get_schema() -> str:
    """
    Returns a string listing:
    - Table names
    - Columns with data types
    - Primary keys
    - Foreign key relationships
    """
    inspector = inspect(engine)

    output = []

    # Get all tables
    tables = inspector.get_table_names()

    for table in tables:
        output.append(f"{table}:")

        # Columns
        columns = inspector.get_columns(table)
        for col in columns:
            col_name = col["name"]
            col_type = str(col["type"])
            output.append(f"  - {col_name} ({col_type})")

        # Primary Keys
        pk = inspector.get_pk_constraint(table)
        pk_cols = pk.get("constrained_columns", [])
        if pk_cols:
            output.append(f"  Primary Key: {', '.join(pk_cols)}")

        # Foreign Keys
        fks = inspector.get_foreign_keys(table)
        for fk in fks:
            local_cols = fk.get("constrained_columns", [])
            ref_table = fk.get("referred_table")
            ref_cols = fk.get("referred_columns", [])

            for lc, rc in zip(local_cols, ref_cols):
                output.append(f"  FK: {table}.{lc} -> {ref_table}.{rc}")

        output.append("")  # blank line between tables

    return "\n".join(output)

def run_query(sql: str, timeout: int = 10):
    """
    Executes a SQL query with timeout and logging.
    Returns:
        {
            "rows": list[dict],
            "execution_time": float,
            "row_count": int
        }
    """
    start_time = time.time()

    try:
        log_sql(sql)

        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = [dict(row._mapping) for row in result]

        execution_time = time.time() - start_time

        # Check timeout
        if execution_time > timeout:
            raise TimeoutError(f"Query exceeded {timeout} seconds")

        row_count = len(rows)

        # Limit rows if more than 100
        if row_count > 100:
            logger.warning(f"Result truncated from {row_count} to 100 rows")
            rows = rows[:100]

        log_execution_time("Query execution", execution_time)

        return {
            "rows": rows,
            "execution_time": execution_time,
            "row_count": row_count
        }

    except Exception as e:
        log_error(str(e))
        raise


if __name__ == "__main__":
    schema = get_schema()
    logger.info(f"Schema loaded:\n{schema}")

    # Test run_query
    results = run_query("SELECT TOP 5 CustomerID, CompanyName, Country FROM Customers")
    
    rows = results["rows"]
    for row in rows:
        logger.info(row)
    
    logger.info(f"Rows returned: {results['row_count']}")
    logger.info(f"Query execution time: {results['execution_time']} seconds")
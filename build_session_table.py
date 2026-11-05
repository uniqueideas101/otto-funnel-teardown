import duckdb

DB_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\outputs\otto.duckdb"
SQL_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\sql\build_session_table.sql"

con = duckdb.connect(DB_PATH)

with open(SQL_PATH, "r") as f:
    query = f.read()

print("Building session_table...")

con.execute(query)

print("session_table created successfully.")

result = con.execute("""
    SELECT
        COUNT(*) AS total_sessions
    FROM session_table;
""").fetchdf()

print(result)

con.close()
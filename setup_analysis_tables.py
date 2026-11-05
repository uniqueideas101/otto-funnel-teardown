import duckdb

DB_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\outputs\otto.duckdb"

con = duckdb.connect(DB_PATH)

with open(
    r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\src\setup_analysis_tables.sql",
    "r"
) as f:
    query = f.read()

con.execute(query)

print("event_table_with_time created successfully.")

con.close()
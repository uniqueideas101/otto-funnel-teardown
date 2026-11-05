import duckdb

DB_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\outputs\otto.duckdb"

con = duckdb.connect(DB_PATH)

with open(
    r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\sql\session_article_journey.sql",
    "r"
) as f:
    query = f.read()

con.execute(query)

print("session_article_journey created successfully.")

con.close()
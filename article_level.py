import duckdb

DB_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\outputs\otto.duckdb"

con = duckdb.connect(DB_PATH)

with open(
    r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\sql\article_metrics.sql",
    "r"
) as file:
    query = file.read()

print("Building article_metrics...")
con.execute(query)

print("article_metrics created successfully.")

print(con.execute("""
    SELECT COUNT(*) AS total_articles
    FROM article_metrics
""").fetchdf())

con.close()
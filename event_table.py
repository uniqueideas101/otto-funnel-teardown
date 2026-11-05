import duckdb

DATA_PATH = r"C:\Users\hp\.cache\kagglehub\competitions\otto-recommender-system\train.jsonl"
DB_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\outputs\otto.duckdb"

con = duckdb.connect(DB_PATH)

query = f"""
CREATE OR REPLACE TABLE event_table AS

SELECT
    s.session,
    u.event_number,
    u.event.aid AS aid,
    u.event.ts AS ts,
    u.event.type AS type
FROM read_json_auto('{DATA_PATH}') AS s
CROSS JOIN UNNEST(s.events) WITH ORDINALITY AS u(event, event_number);
"""

print("Building event_table...")
con.execute(query)

print("event_table created successfully.")

result = con.execute("""
    SELECT
        COUNT(*) AS total_events,
        COUNT(DISTINCT session) AS total_sessions,
        COUNT(DISTINCT aid) AS unique_articles
    FROM event_table;
""").fetchdf()

print("\nEvent table summary:")
print(result)

print("\nEvent types:")
print(con.execute("""
    SELECT
        type,
        COUNT(*) AS event_count
    FROM event_table
    GROUP BY type
    ORDER BY event_count DESC;
""").fetchdf())

con.close()
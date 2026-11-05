import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

con = duckdb.connect(str(ROOT / "outputs" / "otto.duckdb"))

sql = (ROOT / "sql" / "article_journey_metrics.sql").read_text()

con.execute(sql)

print("Created article_journey_metrics")

print(
    con.execute("""
        SELECT *
        FROM article_journey_metrics
        ORDER BY click_sessions DESC
        LIMIT 10
    """).df()
)

con.close()
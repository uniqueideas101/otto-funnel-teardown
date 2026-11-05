CREATE OR REPLACE TABLE session_table AS

SELECT
    session,
    MIN(event_time) AS first_event_time,
    MAX(event_time) AS last_event_time,
    MAX(event_time) - MIN(event_time) AS session_duration
FROM event_table_with_time
GROUP BY session;
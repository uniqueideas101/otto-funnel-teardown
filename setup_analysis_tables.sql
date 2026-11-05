CREATE OR REPLACE TABLE event_table_with_time AS
SELECT
    session,
    event_number,
    aid,
    ts,
    timezone('UTC', to_timestamp(ts / 1000.0)) AS event_time,
    type
FROM event_table;
import duckdb

DB_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\outputs\otto.duckdb"

con = duckdb.connect(DB_PATH)


def session_duration():
    query = """
    SELECT
        session,
        MAX(event_time) - MIN(event_time) AS session_duration
    FROM event_table_with_time
    GROUP BY session;
    """

    return con.execute(query).fetchdf()


def session_span_distribution():
    query = """
    with x as (select epoch(session_duration) as session_duration_seconds from session_table)
    select avg(session_duration_seconds) as avg_session_duration, 
    QUANTILE_CONT(session_duration_seconds, 0.25) AS p25,
    QUANTILE_CONT(session_duration_seconds, 0.75) AS p75,
    QUANTILE_CONT(session_duration_seconds, 0.90) AS p90,
    QUANTILE_CONT(session_duration_seconds, 0.95) AS p95,
    QUANTILE_CONT(session_duration_seconds, 0.99) AS p99,
    MIN(session_duration_seconds) AS min_session_duration,
    MAX(session_duration_seconds) AS max_session_duration,
    median(session_duration_seconds) as median_session_duration from x;
    """

    return con.execute(query).fetchdf()

def time_to_cart():
    query = """
    with first_carts as 
    (select session, min(event_time) as first_cart_time 
    from event_table_with_time
    where type = 'carts' 
    group by session)
    
    select session, min(event_time) as first_event_time, 
    first_cart_time, first_cart_time - min(event_time) 
    as time_to_cart from event_table_with_time 
    join first_carts 
    using (session) 
    group by session, first_cart_time;
    """

    return con.execute(query).fetchdf()

def time_to_cart_validation():
    query = """
    with first_carts as 
    (select session, min(event_time) as first_cart_time 
    from event_table_with_time
    where type = 'carts' 
    group by session), 
    cart_time as (select session, min(event_time) as first_event_time, 
    first_cart_time, first_cart_time - min(event_time) 
    as time_to_cart from event_table_with_time 
    join first_carts 
    using (session) 
    group by session, first_cart_time)
    select count(*) as total_carting_sessions, count(case when epoch(time_to_cart) < 0 then 1 end) as negative_time_to_cart,
    count(case when epoch(time_to_cart) = 0 then 1 end) as zero_time_to_cart
    from cart_time
    """

    return con.execute(query).fetchdf()

def time_to_order():
    query = """
    WITH first_carts AS (
    SELECT session, MIN(event_time) AS first_cart_time
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session),

    first_orders AS (
    SELECT session, MIN(event_time) AS first_order_time
    FROM event_table_with_time
    WHERE type = 'orders'
    GROUP BY session),
    
    first_clicks AS (
    SELECT session, MIN(event_time) AS first_click_time
    FROM event_table_with_time
    WHERE type = 'clicks'
    GROUP BY session),
    
    first_events AS (
    SELECT session, MIN(event_time) AS first_event_time
    FROM event_table_with_time
    GROUP BY session)
    
    SELECT
    first_clicks.session, first_event_time, first_click_time,
    first_cart_time, first_order_time,
    first_cart_time - first_event_time AS time_to_cart,
    first_order_time - first_event_time AS time_to_order,
    first_order_time - first_cart_time AS cart_to_order_time
    FROM first_clicks
    JOIN first_carts USING (session)
    JOIN first_orders USING (session)
    JOIN first_events USING (session)
    WHERE first_click_time < first_cart_time
    AND first_cart_time < first_order_time;
    """

    return con.execute(query).fetchdf()

def time_to_order_validation():
    query = """
WITH first_carts AS (
    SELECT
        session,
        MIN(event_time) AS first_cart_time
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),

first_orders AS (
    SELECT
        session,
        MIN(event_time) AS first_order_time
    FROM event_table_with_time
    WHERE type = 'orders'
    GROUP BY session
),

first_clicks AS (
    SELECT
        session,
        MIN(event_time) AS first_click_time
    FROM event_table_with_time
    WHERE type = 'clicks'
    GROUP BY session
),

first_events AS (
    SELECT
        session,
        MIN(event_time) AS first_event_time
    FROM event_table_with_time
    GROUP BY session
),

funnel_sessions AS (
    SELECT
        first_clicks.session,
        first_event_time,
        first_click_time,
        first_cart_time,
        first_order_time,
        first_cart_time - first_event_time AS time_to_cart,
        first_order_time - first_event_time AS time_to_order,
        first_order_time - first_cart_time AS cart_to_order_time
    FROM first_clicks
    JOIN first_carts USING (session)
    JOIN first_orders USING (session)
    JOIN first_events USING (session)
    WHERE first_click_time < first_cart_time
      AND first_cart_time < first_order_time
),

x as (select session, epoch(time_to_order) as time_to_order_seconds,
epoch(time_to_cart) as time_to_cart_seconds,
epoch(cart_to_order_time) as cart_to_order_seconds
 from funnel_sessions)

/*SELECT
    COUNT(*) AS qualifying_sessions,
    COUNT(CASE WHEN time_to_order < INTERVAL '0 seconds' THEN 1 END) AS negative_time_to_order,
    COUNT(CASE WHEN time_to_order = INTERVAL '0 seconds' THEN 1 END) AS zero_time_to_order,
    MIN(time_to_order) AS min_time_to_order,
    MAX(time_to_order) AS max_time_to_order
    from funnel_sessions*/

    SELECT
    median(time_to_order_seconds) AS median_time_to_order,
    median(time_to_cart_seconds) AS median_time_to_cart,
    median(cart_to_order_seconds) AS median_cart_to_order_time,

    QUANTILE_CONT(time_to_order_seconds, 0.75) AS p75_time_to_order,
    QUANTILE_CONT(time_to_order_seconds, 0.90) AS p90_time_to_order,
    QUANTILE_CONT(time_to_order_seconds, 0.95) AS p95_time_to_order,

    QUANTILE_CONT(time_to_cart_seconds, 0.75) AS p75_time_to_cart,
    QUANTILE_CONT(time_to_cart_seconds, 0.90) AS p90_time_to_cart,
    QUANTILE_CONT(time_to_cart_seconds, 0.95) AS p95_time_to_cart,

    QUANTILE_CONT(cart_to_order_seconds, 0.75) AS p75_cart_to_order,
    QUANTILE_CONT(cart_to_order_seconds, 0.90) AS p90_cart_to_order,
    QUANTILE_CONT(cart_to_order_seconds, 0.95) AS p95_cart_to_order
    FROM x;

    """

    return con.execute(query).fetchdf()

# --------------------------------------------------
# RUN ONLY WHAT YOU WANT
# --------------------------------------------------

result = time_to_order_validation()
print(result.to_string())

con.close()
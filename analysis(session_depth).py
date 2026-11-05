import duckdb

DB_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\outputs\otto.duckdb"

con = duckdb.connect(DB_PATH)

def funnel_baseline():
    query = """ 

SELECT
    COUNT(DISTINCT session) AS total_sessions,
    COUNT(DISTINCT CASE
        WHEN type = 'clicks' THEN session
    END) AS sessions_with_clicks,
    COUNT(DISTINCT CASE
        WHEN type = 'carts' THEN session
    END) AS sessions_with_carts,
    COUNT(DISTINCT CASE
        WHEN type = 'orders' THEN session
    END) AS sessions_with_orders
FROM event_table_with_time;


WITH first_click AS (
    SELECT
        session,
        MIN(event_number) AS first_click_event
    FROM event_table_with_time
    WHERE type = 'clicks'
    GROUP BY session
),

first_cart AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),

first_order AS (
    SELECT
        session,
        MIN(event_number) AS first_order_event
    FROM event_table_with_time
    WHERE type = 'orders'
    GROUP BY session
)

SELECT
    COUNT(DISTINCT CASE
        WHEN fc.first_click_event < fcart.first_cart_event
        THEN fc.session
    END) AS chronological_click_to_cart,

    COUNT(DISTINCT CASE
        WHEN fc.first_click_event < fcart.first_cart_event
         AND fcart.first_cart_event < fo.first_order_event
        THEN fc.session
    END) AS chronological_click_cart_order,

    COUNT(DISTINCT CASE
        WHEN fc.first_click_event < fo.first_order_event
        THEN fc.session
    END) AS chronological_click_to_order
    FROM first_click AS fc
    LEFT JOIN first_cart AS fcart
    USING (session)
    LEFT JOIN first_order AS fo
    USING (session);
    """

    return con.execute(query).fetchdf()

def behavioural_paths():
    query = """
WITH first_click AS (
    SELECT
        session,
        MIN(event_number) AS first_click_event
    FROM event_table_with_time
    WHERE type = 'clicks'
    GROUP BY session
),

first_cart AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),

first_order AS (
    SELECT
        session,
        MIN(event_number) AS first_order_event
    FROM event_table_with_time
    WHERE type = 'orders'
    GROUP BY session
)

SELECT
    COUNT(*) AS ordering_sessions,

    COUNT(CASE
        WHEN first_click_event < first_cart_event
         AND first_cart_event < first_order_event
        THEN 1
    END) AS click_cart_order,

    COUNT(CASE
        WHEN first_click_event < first_order_event
         AND NOT (
             first_click_event < first_cart_event
             AND first_cart_event < first_order_event
         )
        THEN 1
    END) AS click_order_without_strict_funnel,

    COUNT(CASE
        WHEN first_cart_event IS NULL
        THEN 1
    END) AS order_without_cart,

    COUNT(CASE
        WHEN first_click_event IS NULL
        THEN 1
    END) AS order_without_click
    FROM first_order AS fo
    LEFT JOIN first_click AS fc USING (session)
    LEFT JOIN first_cart AS fcart USING (session);
    """
    return con.execute(query).fetchdf()

def click_depth_before_cart():
    query = """
WITH cart_event AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),

click_depth_table AS (
    SELECT
        c.session,
        COUNT(e.event_number) AS click_depth
    FROM cart_event AS c
    LEFT JOIN event_table_with_time AS e
        ON c.session = e.session
        AND e.type = 'clicks'
        AND e.event_number < c.first_cart_event
    GROUP BY c.session
)
select * from click_depth_table;
"""
    return con.execute(query).fetchdf()

def click_depth_before_cart_validation():
    query = """ 
    WITH cart_event AS (
        SELECT
            session,
            MIN(event_number) AS first_cart_event
        FROM event_table_with_time
        WHERE type = 'carts'
        GROUP BY session
    ),
    
    click_depth_table AS (
        SELECT
            c.session,
            COUNT(e.event_number) AS click_depth
        FROM cart_event AS c
        LEFT JOIN event_table_with_time AS e
            ON c.session = e.session
            AND e.type = 'clicks'
            AND e.event_number < c.first_cart_event
        GROUP BY c.session
    )

    SELECT
    MIN(click_depth) AS min_click_depth,
    MAX(click_depth) AS max_click_depth,
    MEDIAN(click_depth) AS median_click_depth,
    AVG(click_depth) AS mean_click_depth,
    COUNT(CASE WHEN click_depth = 0 THEN 1 END) AS zero_click_sessions
    FROM click_depth_table;
    """
    return con.execute(query).fetchdf()

def click_depth_before_cart_distribution():
    query = """
WITH cart_event AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),

click_depth_table AS (
    SELECT
        c.session,
        COUNT(e.event_number) AS click_depth
    FROM cart_event AS c
    LEFT JOIN event_table_with_time AS e
        ON c.session = e.session
        AND e.type = 'clicks'
        AND e.event_number < c.first_cart_event
    GROUP BY c.session
)

select quantile_cont(click_depth, 0.25) as p25_click_depth,
    quantile_cont(click_depth, 0.5) as p50_click_depth,
    quantile_cont(click_depth, 0.75) as p75_click_depth,
    quantile_cont(click_depth, 0.9) as p90_click_depth,
    quantile_cont(click_depth, 0.95) as p95_click_depth,
    quantile_cont(click_depth, 0.99) as p99_click_depth
    from click_depth_table;
    """
    return con.execute(query).fetchdf()

def click_depth_before_order():
    query = """
WITH first_click AS (
    SELECT
        session,
        MIN(event_number) AS first_click_event
    FROM event_table_with_time
    WHERE type = 'clicks'
    GROUP BY session
),

first_cart AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),

first_order AS (
    SELECT
        session,
        MIN(event_number) AS first_order_event
    FROM event_table_with_time
    WHERE type = 'orders'
    GROUP BY session
),

funnel_sessions AS (
    SELECT
        fc.session,
        fc.first_click_event,
        fcart.first_cart_event,
        fo.first_order_event
    FROM first_click AS fc
    JOIN first_cart AS fcart
        USING (session)
    JOIN first_order AS fo
        USING (session)
    WHERE fc.first_click_event < fcart.first_cart_event
      AND fcart.first_cart_event < fo.first_order_event
)

SELECT
    f.session,

    COUNT(CASE
        WHEN e.type = 'clicks'
         AND e.event_number < f.first_order_event
        THEN 1
    END) AS clicks_before_order,

    COUNT(CASE
        WHEN e.type = 'carts'
         AND e.event_number < f.first_order_event
        THEN 1
    END) AS carts_before_order,

    COUNT(CASE
        WHEN e.event_number < f.first_order_event
        THEN 1
    END) AS total_events_before_order

FROM funnel_sessions AS f
JOIN event_table_with_time AS e
    ON f.session = e.session
GROUP BY f.session;"""
    return con.execute(query).fetchdf()

def click_depth_before_order_validation():
    query = """
WITH first_click AS (
    SELECT
        session,
        MIN(event_number) AS first_click_event
    FROM event_table_with_time
    WHERE type = 'clicks'
    GROUP BY session
),

first_cart AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),

first_order AS (
    SELECT
        session,
        MIN(event_number) AS first_order_event
    FROM event_table_with_time
    WHERE type = 'orders'
    GROUP BY session
),

funnel_sessions AS (
    SELECT
        fc.session,
        fc.first_click_event,
        fcart.first_cart_event,
        fo.first_order_event
    FROM first_click AS fc
    JOIN first_cart AS fcart
        USING (session)
    JOIN first_order AS fo
        USING (session)
    WHERE fc.first_click_event < fcart.first_cart_event
      AND fcart.first_cart_event < fo.first_order_event
),

depth AS (
    SELECT
        f.session,

        COUNT(CASE
            WHEN e.type = 'clicks'
             AND e.event_number < f.first_order_event
            THEN 1
        END) AS clicks_before_order,

        COUNT(CASE
            WHEN e.type = 'carts'
             AND e.event_number < f.first_order_event
            THEN 1
        END) AS carts_before_order,

        COUNT(CASE
            WHEN e.event_number < f.first_order_event
            THEN 1
        END) AS total_events_before_order

    FROM funnel_sessions AS f
    JOIN event_table_with_time AS e
        ON f.session = e.session
    GROUP BY f.session
)

SELECT
    COUNT(*) AS sessions,

    MEDIAN(clicks_before_order) AS median_clicks,
    QUANTILE_CONT(clicks_before_order, 0.75) AS p75_clicks,
    QUANTILE_CONT(clicks_before_order, 0.90) AS p90_clicks,
    QUANTILE_CONT(clicks_before_order, 0.95) AS p95_clicks,

    MEDIAN(carts_before_order) AS median_carts,
    QUANTILE_CONT(carts_before_order, 0.75) AS p75_carts,
    QUANTILE_CONT(carts_before_order, 0.90) AS p90_carts,
    QUANTILE_CONT(carts_before_order, 0.95) AS p95_carts,

    MEDIAN(total_events_before_order) AS median_events,
    QUANTILE_CONT(total_events_before_order, 0.75) AS p75_events,
    QUANTILE_CONT(total_events_before_order, 0.90) AS p90_events,
    QUANTILE_CONT(total_events_before_order, 0.95) AS p95_events

FROM depth;
"""

    return con.execute(query).fetchdf()

def order_vs_nonorder_session_depth():
    query = """ 
WITH session_depth AS (
    SELECT
        session,

        MAX(CASE
            WHEN type = 'orders' THEN 1
            ELSE 0
        END) AS ordered,

        COUNT(CASE
            WHEN type = 'clicks' THEN 1
        END) AS click_count,

        COUNT(CASE
            WHEN type = 'carts' THEN 1
        END) AS cart_count,

        COUNT(CASE
            WHEN type IN ('clicks', 'carts') THEN 1
        END) AS interaction_count

    FROM event_table_with_time
    GROUP BY session
)

SELECT
    CASE
        WHEN ordered = 1 THEN 'ordering'
        ELSE 'non_ordering'
    END AS session_group,

    COUNT(*) AS sessions,

    MEDIAN(click_count) AS median_clicks,
    QUANTILE_CONT(click_count, 0.75) AS p75_clicks,
    QUANTILE_CONT(click_count, 0.90) AS p90_clicks,

    MEDIAN(cart_count) AS median_carts,
    QUANTILE_CONT(cart_count, 0.75) AS p75_carts,
    QUANTILE_CONT(cart_count, 0.90) AS p90_carts,

    MEDIAN(interaction_count) AS median_interactions,
    QUANTILE_CONT(interaction_count, 0.75) AS p75_interactions,
    QUANTILE_CONT(interaction_count, 0.90) AS p90_interactions

FROM session_depth
GROUP BY ordered
ORDER BY ordered DESC;
"""
    return con.execute(query).fetchdf()

result = order_vs_nonorder_session_depth()
print(result.to_string())

con.close()
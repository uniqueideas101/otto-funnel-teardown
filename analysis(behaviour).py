import duckdb

DB_PATH = r"C:\Users\hp\OneDrive\Documents\otto_funnel_teardown\outputs\otto.duckdb"

con = duckdb.connect(DB_PATH)

def session_journey_classification():
    query = """
    with session_milestones as (
    select session, 
    min(case when type = 'clicks' then event_number end) as first_click,
    min(case when type = 'carts' then event_number end) as first_cart,
    min(case when type = 'orders' then event_number end) as first_order
    from event_table_with_time
    group by session
    ),
    session_classification AS (
    SELECT
        session,

        CASE
            WHEN first_click < first_cart
             AND first_cart < first_order
                THEN 'click_cart_order'

            WHEN first_click < first_order
             AND first_cart IS NULL
                THEN 'click_order_no_cart'

            WHEN first_cart < first_order
             AND first_click IS NULL
                THEN 'cart_order'

            WHEN first_click IS NOT NULL
             AND first_cart IS NULL
             AND first_order IS NULL
                THEN 'click_only'

            WHEN first_click < first_cart
             AND first_order IS NULL
                THEN 'click_cart_no_order'

            WHEN first_click IS NULL
             AND first_cart IS NOT NULL
             AND first_order IS NULL
                THEN 'cart_only'

            ELSE 'other'

        END AS journey_type

    FROM session_milestones)

    SELECT
    journey_type,
    COUNT(*) AS session_count
    FROM session_classification
    GROUP BY journey_type
    ORDER BY session_count DESC;


    """
    return con.execute(query).fetchdf()

def classification_other():
    query = """
    with session_milestones as (
    select session, 
    min(case when type = 'clicks' then event_number end) as first_click,
    min(case when type = 'carts' then event_number end) as first_cart,
    min(case when type = 'orders' then event_number end) as first_order
    from event_table_with_time
    group by session
    ),
    session_classification AS (
    SELECT
        session, first_click,
        first_cart,
        first_order,
        CASE
            WHEN first_click < first_cart
             AND first_cart < first_order
                THEN 'click_cart_order'

            WHEN first_click < first_order
             AND first_cart IS NULL
                THEN 'click_order_no_cart'

            WHEN first_cart < first_order
             AND first_click IS NULL
                THEN 'cart_order'

            WHEN first_click IS NOT NULL
             AND first_cart IS NULL
             AND first_order IS NULL
                THEN 'click_only'

            WHEN first_click < first_cart
             AND first_order IS NULL
                THEN 'click_cart_no_order'

            WHEN first_click IS NULL
             AND first_cart IS NOT NULL
             AND first_order IS NULL
                THEN 'cart_only'

            ELSE 'other'

        END AS journey_type

    FROM session_milestones)

    SELECT
    CASE
        WHEN first_cart < first_click
         AND first_order > first_cart
            THEN 'cart_click_order'

        WHEN first_cart < first_click
         AND first_order IS NULL
            THEN 'cart_click_no_order'

        WHEN first_order < first_cart
         AND first_cart < first_click
            THEN 'order_cart_click'

        WHEN first_order < first_click
         AND (first_cart IS NULL OR first_order < first_cart)
            THEN 'order_before_click'

        ELSE 'other_unclassified'
    END AS other_path,
    COUNT(*) AS sessions
    FROM session_classification
    WHERE journey_type = 'other'
    GROUP BY other_path
    ORDER BY sessions DESC;


    """
    return con.execute(query).fetchdf()

def article_level_analysis():
    query = """
    SELECT
    aid,
    click_sessions,
    click_events,
    cart_sessions,
    order_sessions
FROM article_metrics
ORDER BY click_sessions DESC
LIMIT 20;
    """
    return con.execute(query).fetchdf()

def aid_rates():
    query = """
    SELECT
    *
    FROM article_metrics
    WHERE click_sessions >= 1000
    ORDER BY click_to_cart_rate DESC
    LIMIT 20;
    """
    return con.execute(query).fetchdf()

def chronological_article_analysis():
    query = """
    SELECT
    aid,
    click_sessions,
    click_then_cart_sessions,
    click_cart_order_sessions,

    ROUND(
        100.0 * click_then_cart_sessions
        / NULLIF(click_sessions, 0), 2
    ) AS click_cart_progression_pct,

    ROUND(
        100.0 * click_cart_order_sessions
        / NULLIF(click_sessions, 0), 2
    ) AS full_journey_pct

FROM article_journey_metrics

WHERE click_sessions >= 1000

ORDER BY click_cart_order_sessions DESC

LIMIT 20; 
    """
    return con.execute(query).fetchdf()

def multiple_article_analysis():
    query = """
    SELECT
    COUNT(*) AS total_click_cart_order_sessions,

    COUNT(CASE
        WHEN first_click_aid = first_cart_aid
         AND first_cart_aid = first_order_aid
        THEN 1 END) AS same_article_all_stages,

    COUNT(CASE
        WHEN first_click_aid <> first_cart_aid
          OR first_cart_aid <> first_order_aid
        THEN 1 END) AS switched_article_at_least_once,

    ROUND(
        100.0 * COUNT(CASE
            WHEN first_click_aid = first_cart_aid
             AND first_cart_aid = first_order_aid
            THEN 1 END) / NULLIF(COUNT(*), 0), 2
    ) AS same_article_pct,

    ROUND(
        100.0 * COUNT(CASE
            WHEN first_click_aid <> first_cart_aid
              OR first_cart_aid <> first_order_aid
            THEN 1 END) / NULLIF(COUNT(*), 0), 2
    ) AS switched_article_pct

FROM session_article_journeys
WHERE first_click_event < first_cart_event
  AND first_cart_event < first_order_event;
    """
    return con.execute(query).fetchdf()

def multiple_article_analysis_1():
    query = """
    SELECT
    COUNT(CASE
        WHEN first_click_event < first_cart_event
        THEN 1 END) AS chronological_click_cart_sessions,

    COUNT(CASE
        WHEN first_click_event < first_cart_event
         AND first_click_aid = first_cart_aid
        THEN 1 END) AS same_article_click_cart,

    COUNT(CASE
        WHEN first_click_event < first_cart_event
         AND first_click_aid <> first_cart_aid
        THEN 1 END) AS switched_article_click_cart,

    COUNT(CASE
        WHEN first_cart_event < first_order_event
        THEN 1 END) AS chronological_cart_order_sessions,

    COUNT(CASE
        WHEN first_cart_event < first_order_event
         AND first_cart_aid = first_order_aid
        THEN 1 END) AS same_article_cart_order,

    COUNT(CASE
        WHEN first_cart_event < first_order_event
         AND first_cart_aid <> first_order_aid
        THEN 1 END) AS switched_article_cart_order

FROM session_article_journeys; """
    return con.execute(query).fetchdf()

def multiple_article_analysis_2():
    query = """
    WITH article_counts AS (
    SELECT
        e.session,
        COUNT(DISTINCT e.aid) AS distinct_articles_before_order

    FROM event_table_with_time e
    JOIN session_article_journeys j
        ON e.session = j.session

    WHERE j.first_order_event IS NOT NULL
      AND e.event_number <= j.first_order_event

    GROUP BY e.session
)

SELECT
    COUNT(*) AS ordering_sessions,

    ROUND(AVG(distinct_articles_before_order), 2) AS mean_articles,

    MEDIAN(distinct_articles_before_order) AS median_articles,

    QUANTILE_CONT(distinct_articles_before_order, 0.75) AS p75_articles,

    QUANTILE_CONT(distinct_articles_before_order, 0.90) AS p90_articles,

    MAX(distinct_articles_before_order) AS max_articles
    FROM article_counts;
    """
    return con.execute(query).fetchdf()

def multiple_article_analysis_3():
    query = """
    WITH article_counts AS (
    SELECT
        e.session,
        COUNT(DISTINCT e.aid) AS distinct_articles

    FROM event_table_with_time e
    JOIN session_article_journeys j
        ON e.session = j.session

    WHERE j.first_order_event IS NOT NULL
      AND e.event_number <= j.first_order_event

    GROUP BY e.session
)

SELECT
    CASE
        WHEN distinct_articles = 1 THEN '1 article'
        WHEN distinct_articles = 2 THEN '2 articles'
        WHEN distinct_articles = 3 THEN '3 articles'
        WHEN distinct_articles = 4 THEN '4 articles'
        WHEN distinct_articles = 5 THEN '5 articles'
        ELSE '6+ articles'
    END AS article_count_group,

    COUNT(*) AS sessions,

    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2
    ) AS session_pct

FROM article_counts
GROUP BY article_count_group
ORDER BY
    CASE article_count_group
        WHEN '1 article' THEN 1
        WHEN '2 articles' THEN 2
        WHEN '3 articles' THEN 3
        WHEN '4 articles' THEN 4
        WHEN '5 articles' THEN 5
        ELSE 6
    END;
    """
    return con.execute(query).fetchdf()

def multiple_article_analysis_4():
    query = """
    WITH ordered_events AS (
    SELECT
        e.session,
        e.event_number,
        e.aid,

        LAG(e.aid) OVER (
            PARTITION BY e.session
            ORDER BY e.event_number
        ) AS previous_aid,

        j.first_order_event

    FROM event_table_with_time e
    JOIN session_article_journeys j
        ON e.session = j.session

    WHERE j.first_order_event IS NOT NULL
      AND e.event_number <= j.first_order_event
),

switch_counts AS (
    SELECT
        session,

        COUNT(CASE
            WHEN previous_aid IS NOT NULL
             AND aid <> previous_aid
            THEN 1 END) AS article_switches

    FROM ordered_events
    GROUP BY session
)

SELECT
    COUNT(*) AS ordering_sessions,

    ROUND(AVG(article_switches), 2) AS mean_switches,

    MEDIAN(article_switches) AS median_switches,

    QUANTILE_CONT(article_switches, 0.75) AS p75_switches,

    QUANTILE_CONT(article_switches, 0.90) AS p90_switches,

    MAX(article_switches) AS max_switches

FROM switch_counts; """
    return con.execute(query).fetchdf()

def daily_shopping_activity():
    query = """
    WITH session_day AS (
    SELECT
        CAST(event_time AS DATE) AS activity_date,
        session,

        COUNT(CASE WHEN type = 'clicks' THEN 1 END) AS clicks,
        COUNT(CASE WHEN type = 'carts' THEN 1 END) AS carts,
        COUNT(CASE WHEN type = 'orders' THEN 1 END) AS orders,

        COUNT(*) AS total_events

    FROM event_table_with_time
    GROUP BY
        CAST(event_time AS DATE),
        session
)

SELECT
    activity_date,

    COUNT(*) AS active_sessions,

    SUM(clicks) AS click_events,
    SUM(carts) AS cart_events,
    SUM(orders) AS order_events,

    ROUND(AVG(clicks), 2) AS clicks_per_session,
    ROUND(AVG(carts), 2) AS carts_per_session,
    ROUND(AVG(orders), 2) AS orders_per_session,

    ROUND(
        100.0 * COUNT(CASE WHEN carts > 0 THEN 1 END)
        / COUNT(*), 2
    ) AS sessions_with_cart_pct,

    ROUND(
        100.0 * COUNT(CASE WHEN orders > 0 THEN 1 END)
        / COUNT(*), 2
    ) AS sessions_with_order_pct

FROM session_day
GROUP BY activity_date
ORDER BY activity_date; """
    return con.execute(query).fetchdf()

def weekly_shopping_patterns():
    query = """
    WITH session_day AS (
    SELECT
        CAST(event_time AS DATE) AS activity_date,
        session,

        COUNT(CASE WHEN type = 'clicks' THEN 1 END) AS clicks,
        COUNT(CASE WHEN type = 'carts' THEN 1 END) AS carts,
        COUNT(CASE WHEN type = 'orders' THEN 1 END) AS orders

    FROM event_table_with_time

    WHERE event_time >= TIMESTAMP '2022-08-01 00:00:00'
      AND event_time < TIMESTAMP '2022-08-28 00:00:00'

    GROUP BY activity_date, session
),

daily_metrics AS (
    SELECT
        activity_date,
        STRFTIME(activity_date, '%A') AS weekday,
        EXTRACT(DOW FROM activity_date) AS weekday_number,

        COUNT(*) AS active_sessions,
        SUM(clicks) AS click_events,
        SUM(carts) AS cart_events,
        SUM(orders) AS order_events,

        AVG(clicks) AS clicks_per_session,
        AVG(carts) AS carts_per_session,
        AVG(orders) AS orders_per_session

    FROM session_day
    GROUP BY activity_date
)

SELECT
    weekday,
    COUNT(*) AS number_of_days,

    ROUND(AVG(active_sessions), 0) AS avg_daily_active_sessions,
    ROUND(AVG(click_events), 0) AS avg_daily_click_events,
    ROUND(AVG(cart_events), 0) AS avg_daily_cart_events,
    ROUND(AVG(order_events), 0) AS avg_daily_order_events,

    ROUND(AVG(clicks_per_session), 2) AS avg_clicks_per_session,
    ROUND(AVG(carts_per_session), 2) AS avg_carts_per_session,
    ROUND(AVG(orders_per_session), 2) AS avg_orders_per_session

FROM daily_metrics
GROUP BY weekday, weekday_number
ORDER BY weekday_number; """
    return con.execute(query).fetchdf()


def hourly_shopping_patterns():
    query = """
    WITH session_hour AS (
    SELECT
        CAST(event_time AS DATE) AS activity_date,

        EXTRACT(HOUR FROM event_time) AS hour_of_day,

        session,

        COUNT(CASE WHEN type = 'clicks' THEN 1 END) AS clicks,
        COUNT(CASE WHEN type = 'carts' THEN 1 END) AS carts,
        COUNT(CASE WHEN type = 'orders' THEN 1 END) AS orders

    FROM event_table_with_time
    GROUP BY
        CAST(event_time AS DATE),
        EXTRACT(HOUR FROM event_time),
        session
),

hourly_daily_metrics AS (
    SELECT
        activity_date,
        hour_of_day,

        COUNT(*) AS active_sessions,

        SUM(clicks) AS click_events,
        SUM(carts) AS cart_events,
        SUM(orders) AS order_events,

        AVG(clicks) AS clicks_per_session,
        AVG(carts) AS carts_per_session,
        AVG(orders) AS orders_per_session,

        100.0 * COUNT(CASE WHEN carts > 0 THEN 1 END)
        / COUNT(*) AS cart_session_pct,

        100.0 * COUNT(CASE WHEN orders > 0 THEN 1 END)
        / COUNT(*) AS order_session_pct

    FROM session_hour
    GROUP BY activity_date, hour_of_day
)

SELECT
    hour_of_day,

    COUNT(*) AS number_of_days,

    ROUND(AVG(active_sessions), 0) AS avg_active_sessions,

    ROUND(AVG(click_events), 0) AS avg_click_events,
    ROUND(AVG(cart_events), 0) AS avg_cart_events,
    ROUND(AVG(order_events), 0) AS avg_order_events,

    ROUND(AVG(clicks_per_session), 2) AS avg_clicks_per_session,
    ROUND(AVG(carts_per_session), 2) AS avg_carts_per_session,
    ROUND(AVG(orders_per_session), 2) AS avg_orders_per_session,

    ROUND(AVG(cart_session_pct), 2) AS avg_cart_session_pct,
    ROUND(AVG(order_session_pct), 2) AS avg_order_session_pct

FROM hourly_daily_metrics
GROUP BY hour_of_day
ORDER BY hour_of_day;
    """
    return con.execute(query).fetchdf()

def weekday_hour_activity():
    query = """
    SELECT
    STRFTIME(CAST(event_time AS DATE), '%A') AS weekday,

    EXTRACT(DOW FROM event_time) AS weekday_number,

    EXTRACT(HOUR FROM event_time) AS hour_of_day,

    COUNT(DISTINCT session) AS active_sessions,

    COUNT(CASE WHEN type = 'clicks' THEN 1 END) AS click_events,

    COUNT(CASE WHEN type = 'carts' THEN 1 END) AS cart_events,

    COUNT(CASE WHEN type = 'orders' THEN 1 END) AS order_events

FROM event_table_with_time

GROUP BY
    weekday,
    weekday_number,
    hour_of_day

ORDER BY
    weekday_number,
    hour_of_day;
    """
    return con.execute(query).fetchdf()

def daily_article_popularity():
    query = """
    WITH daily_article_metrics AS (
    SELECT
        CAST(event_time AS DATE) AS activity_date,
        aid,

        COUNT(DISTINCT CASE
            WHEN type = 'clicks' THEN session
        END) AS click_sessions,

        COUNT(DISTINCT CASE
            WHEN type = 'carts' THEN session
        END) AS cart_sessions,

        COUNT(DISTINCT CASE
            WHEN type = 'orders' THEN session
        END) AS order_sessions

    FROM event_table_with_time
    GROUP BY
        CAST(event_time AS DATE),
        aid
),

ranked_articles AS (
    SELECT
        *,

        ROW_NUMBER() OVER (
            PARTITION BY activity_date
            ORDER BY click_sessions DESC
        ) AS daily_rank

    FROM daily_article_metrics
)

SELECT
    activity_date,
    daily_rank,
    aid,
    click_sessions,
    cart_sessions,
    order_sessions

FROM ranked_articles
WHERE daily_rank <= 10

ORDER BY activity_date, daily_rank;
    """
    return con.execute(query).fetchdf()

def distinct_article_before_first_cart():
    query = """
    WITH first_cart AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),
session_metrics AS (
    SELECT
        e.session,
        COUNT(DISTINCT e.aid) AS distinct_articles_clicked,
        COUNT(*) AS click_events_before_cart
    FROM event_table_with_time e
    JOIN first_cart fc
        ON e.session = fc.session
    WHERE e.type = 'clicks'
      AND e.event_number < fc.first_cart_event
    GROUP BY e.session
)
SELECT
    COUNT(*) AS sessions_with_prior_clicks,
    ROUND(AVG(distinct_articles_clicked), 2) AS avg_distinct_articles,
    MEDIAN(distinct_articles_clicked) AS median_distinct_articles,
    QUANTILE_CONT(distinct_articles_clicked, 0.75) AS p75_distinct_articles,
    QUANTILE_CONT(distinct_articles_clicked, 0.90) AS p90_distinct_articles,
    MAX(distinct_articles_clicked) AS max_distinct_articles
FROM session_metrics;
    """
    return con.execute(query).fetchdf()

def repeated_clicks_before_cart():
    query = """
    WITH first_cart AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),
article_clicks AS (
    SELECT
        e.session,
        e.aid,
        COUNT(*) AS clicks_on_article
    FROM event_table_with_time e
    JOIN first_cart fc
        ON e.session = fc.session
    WHERE e.type = 'clicks'
      AND e.event_number < fc.first_cart_event
    GROUP BY e.session, e.aid
),
session_metrics AS (
    SELECT
        session,
        SUM(clicks_on_article) AS total_clicks,
        COUNT(*) AS distinct_articles,
        SUM(clicks_on_article - 1) AS repeat_clicks,
        MAX(clicks_on_article) AS max_clicks_on_one_article
    FROM article_clicks
    GROUP BY session
)
SELECT
    COUNT(*) AS sessions,
    ROUND(AVG(total_clicks), 2) AS avg_total_clicks,
    ROUND(AVG(distinct_articles), 2) AS avg_distinct_articles,
    ROUND(AVG(repeat_clicks), 2) AS avg_repeat_clicks,
    MEDIAN(repeat_clicks) AS median_repeat_clicks,
    QUANTILE_CONT(repeat_clicks, 0.75) AS p75_repeat_clicks,
    QUANTILE_CONT(repeat_clicks, 0.90) AS p90_repeat_clicks,
    MAX(max_clicks_on_one_article) AS max_clicks_on_single_article
FROM session_metrics; """
    return con.execute(query).fetchdf()

def repeated_clicks_distribution():
    query = """
    WITH first_cart AS (
    SELECT
        session,
        MIN(event_number) AS first_cart_event
    FROM event_table_with_time
    WHERE type = 'carts'
    GROUP BY session
),
article_clicks AS (
    SELECT
        e.session,
        e.aid,
        COUNT(*) AS clicks_on_article
    FROM event_table_with_time e
    JOIN first_cart fc
        ON e.session = fc.session
    WHERE e.type = 'clicks'
      AND e.event_number < fc.first_cart_event
    GROUP BY e.session, e.aid
),
session_metrics AS (
    SELECT
        session,
        SUM(clicks_on_article) AS total_clicks,
        COUNT(*) AS distinct_articles,
        SUM(clicks_on_article - 1) AS repeat_clicks
    FROM article_clicks
    GROUP BY session
)
SELECT
    CASE
        WHEN repeat_clicks = 0 THEN '0 - No repeat clicks'
        WHEN repeat_clicks = 1 THEN '1 - One repeat click'
        WHEN repeat_clicks BETWEEN 2 AND 4 THEN '2 - 2 to 4 repeat clicks'
        WHEN repeat_clicks BETWEEN 5 AND 9 THEN '3 - 5 to 9 repeat clicks'
        ELSE '4 - 10+ repeat clicks'
    END AS repeat_click_group,
    COUNT(*) AS sessions,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS session_percentage
    FROM session_metrics
    GROUP BY repeat_click_group
    ORDER BY repeat_click_group;
    """
    return con.execute(query).fetchdf()

def cart_reaching_vs_noncart():
    query = """
WITH session_flags AS (
    SELECT
        session,
        MIN(CASE WHEN type = 'carts'
                 THEN event_number END) AS first_cart_event
    FROM event_table_with_time
    GROUP BY session
),
article_clicks AS (
    SELECT
        e.session,
        e.aid,
        COUNT(*) AS clicks_on_article
    FROM event_table_with_time e
    JOIN session_flags sf
        ON e.session = sf.session
    WHERE e.type = 'clicks'
      AND (
          (sf.first_cart_event IS NOT NULL
           AND e.event_number < sf.first_cart_event)
          OR
          sf.first_cart_event IS NULL
      )
    GROUP BY e.session, e.aid
),
session_metrics AS (
    SELECT
        session,
        SUM(clicks_on_article) AS total_clicks,
        COUNT(*) AS distinct_articles,
        SUM(clicks_on_article - 1) AS repeat_clicks
    FROM article_clicks
    GROUP BY session
),
grouped AS (
    SELECT
        CASE
            WHEN sf.first_cart_event IS NOT NULL
                THEN 'Cart-reaching'
            ELSE 'No-cart'
        END AS session_group,
        sm.session,
        sm.total_clicks,
        sm.distinct_articles,
        sm.repeat_clicks
    FROM session_metrics sm
    JOIN session_flags sf
        ON sm.session = sf.session
)
SELECT
    session_group,
    COUNT(*) AS sessions,
    ROUND(AVG(total_clicks), 2) AS avg_clicks,
    MEDIAN(total_clicks) AS median_clicks,
    ROUND(AVG(distinct_articles), 2) AS avg_distinct_articles,
    MEDIAN(distinct_articles) AS median_distinct_articles,
    ROUND(AVG(repeat_clicks), 2) AS avg_repeat_clicks,
    MEDIAN(repeat_clicks) AS median_repeat_clicks,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE repeat_clicks > 0)
        / COUNT(*),
        2
    ) AS pct_sessions_with_repeat_clicks
FROM grouped
GROUP BY session_group
ORDER BY session_group;
    """
    return con.execute(query).fetchdf()

def close_connection():
    query = """
select * from event_table_with_time limit 20;"""
    return con.execute(query).fetchdf()


result = close_connection()
print(result.to_string())
    
con.close()

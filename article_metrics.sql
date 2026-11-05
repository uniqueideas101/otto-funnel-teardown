
CREATE OR REPLACE TABLE article_metrics AS

SELECT
    aid,

    -- Distinct sessions
    COUNT(DISTINCT CASE
        WHEN type = 'clicks' THEN session
    END) AS click_sessions,

    COUNT(DISTINCT CASE
        WHEN type = 'carts' THEN session
    END) AS cart_sessions,

    COUNT(DISTINCT CASE
        WHEN type = 'orders' THEN session
    END) AS order_sessions,

    -- Total events
    COUNT(CASE
        WHEN type = 'clicks' THEN 1
    END) AS click_events,

    COUNT(CASE
        WHEN type = 'carts' THEN 1
    END) AS cart_events,

    COUNT(CASE
        WHEN type = 'orders' THEN 1
    END) AS order_events,

    -- Session-presence rates
    ROUND(
        100.0 * COUNT(DISTINCT CASE
            WHEN type = 'carts' THEN session
        END)
        / NULLIF(COUNT(DISTINCT CASE
            WHEN type = 'clicks' THEN session
        END), 0),
        2
    ) AS click_to_cart_rate,

    ROUND(
        100.0 * COUNT(DISTINCT CASE
            WHEN type = 'orders' THEN session
        END)
        / NULLIF(COUNT(DISTINCT CASE
            WHEN type = 'carts' THEN session
        END), 0),
        2
    ) AS cart_to_order_rate

FROM event_table_with_time
GROUP BY aid;

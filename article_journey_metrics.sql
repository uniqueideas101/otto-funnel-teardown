CREATE OR REPLACE TABLE article_journey_metrics AS

WITH session_article_milestones AS (
    SELECT
        session,
        aid,

        MIN(CASE WHEN type = 'clicks'
            THEN event_number END) AS first_click,

        MIN(CASE WHEN type = 'carts'
            THEN event_number END) AS first_cart,

        MIN(CASE WHEN type = 'orders'
            THEN event_number END) AS first_order

    FROM event_table_with_time
    GROUP BY session, aid
)

SELECT
    aid,

    COUNT(CASE WHEN first_click IS NOT NULL
        THEN 1 END) AS click_sessions,

    COUNT(CASE WHEN first_cart IS NOT NULL
        THEN 1 END) AS cart_sessions,

    COUNT(CASE WHEN first_order IS NOT NULL
        THEN 1 END) AS order_sessions,

    COUNT(CASE WHEN first_click IS NOT NULL
                AND first_cart IS NOT NULL
                AND first_click < first_cart
        THEN 1 END) AS click_then_cart_sessions,

    COUNT(CASE WHEN first_click IS NOT NULL
                AND first_cart IS NOT NULL
                AND first_order IS NOT NULL
                AND first_click < first_cart
                AND first_cart < first_order
        THEN 1 END) AS click_cart_order_sessions,

    COUNT(CASE WHEN first_cart IS NOT NULL
                AND first_order IS NOT NULL
                AND first_cart < first_order
        THEN 1 END) AS cart_then_order_sessions

FROM session_article_milestones
GROUP BY aid;
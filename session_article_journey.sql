CREATE OR REPLACE TABLE session_article_journeys AS

WITH first_milestones AS (
    SELECT
        session,

        MIN(CASE WHEN type = 'clicks'
            THEN event_number END) AS first_click_event,

        MIN(CASE WHEN type = 'carts'
            THEN event_number END) AS first_cart_event,

        MIN(CASE WHEN type = 'orders'
            THEN event_number END) AS first_order_event

    FROM event_table_with_time
    GROUP BY session
),

milestone_articles AS (
    SELECT
        m.session,
        m.first_click_event,
        m.first_cart_event,
        m.first_order_event,

        MAX(CASE WHEN e.type = 'clicks'
                  AND e.event_number = m.first_click_event
            THEN e.aid END) AS first_click_aid,

        MAX(CASE WHEN e.type = 'carts'
                  AND e.event_number = m.first_cart_event
            THEN e.aid END) AS first_cart_aid,

        MAX(CASE WHEN e.type = 'orders'
                  AND e.event_number = m.first_order_event
            THEN e.aid END) AS first_order_aid

    FROM first_milestones m
    JOIN event_table_with_time e
        ON m.session = e.session
    GROUP BY
        m.session,
        m.first_click_event,
        m.first_cart_event,
        m.first_order_event
)

SELECT *
FROM milestone_articles;
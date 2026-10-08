-- Dialect note: adapt named bind syntax and date arithmetic to your SQL engine.
-- Contract: the source sequence is stable and uniquely orders corrections per order.
WITH ranked_orders AS (
    SELECT
        order_id,
        customer_id,
        order_date,
        status,
        amount,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY source_sequence DESC, updated_at DESC, order_id
        ) AS revision_rank
    FROM orders
    WHERE order_date < CAST(:as_of_date AS DATE) + INTERVAL '1' DAY
),
current_orders AS (
    SELECT order_id, customer_id, order_date, status, amount
    FROM ranked_orders
    WHERE revision_rank = 1
),
customer_spend AS (
    SELECT
        customer_id,
        SUM(amount) AS spend_90d,
        COUNT(*) AS completed_order_count
    FROM current_orders
    WHERE status = 'completed'
      AND order_date >= CAST(:as_of_date AS DATE) - INTERVAL '89' DAY
      AND order_date < CAST(:as_of_date AS DATE) + INTERVAL '1' DAY
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    COALESCE(s.spend_90d, 0) AS spend_90d,
    COALESCE(s.completed_order_count, 0) AS completed_order_count
FROM customers AS c
LEFT JOIN customer_spend AS s
    ON s.customer_id = c.customer_id
ORDER BY c.customer_id;

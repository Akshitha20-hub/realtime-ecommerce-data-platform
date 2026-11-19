-- ============================================================
-- ANALYTICS QUERY 9: Repeat Customers (more than 1 order)
-- ============================================================
SELECT
    repeat_flag,
    COUNT(*) AS customer_count
FROM (
    SELECT
        customer_id,
        CASE WHEN COUNT(DISTINCT order_id) > 1 THEN 'Repeat' ELSE 'One-Time' END AS repeat_flag
    FROM orders
    WHERE order_status IN ('completed', 'shipped')
    GROUP BY customer_id
) sub
GROUP BY repeat_flag;

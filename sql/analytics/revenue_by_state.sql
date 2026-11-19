-- ============================================================
-- ANALYTICS QUERY 10: Revenue by State (Geographic)
-- ============================================================
SELECT
    shipping_state                         AS state,
    COUNT(DISTINCT order_id)               AS total_orders,
    ROUND(SUM(total_amount)::NUMERIC, 2)   AS total_revenue
FROM orders
WHERE order_status IN ('completed', 'shipped')
GROUP BY shipping_state
ORDER BY total_revenue DESC
LIMIT 20;

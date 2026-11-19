-- ============================================================
-- ANALYTICS QUERY 1: Total Revenue (completed + shipped orders)
-- ============================================================
SELECT
    SUM(total_amount)                          AS total_revenue,
    COUNT(DISTINCT order_id)                   AS total_orders,
    ROUND(AVG(total_amount)::NUMERIC, 2)       AS avg_order_value
FROM orders
WHERE order_status IN ('completed', 'shipped');

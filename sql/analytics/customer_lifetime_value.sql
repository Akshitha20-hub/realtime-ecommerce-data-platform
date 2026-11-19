-- ============================================================
-- ANALYTICS QUERY 5: Customer Lifetime Value (CLV)
-- ============================================================
SELECT
    c.customer_id,
    c.first_name || ' ' || c.last_name   AS customer_name,
    c.customer_segment,
    c.city,
    c.state,
    COUNT(DISTINCT o.order_id)           AS total_orders,
    ROUND(SUM(o.total_amount)::NUMERIC, 2) AS lifetime_value,
    ROUND(AVG(o.total_amount)::NUMERIC, 2) AS avg_order_value
FROM customers c
JOIN orders    o ON c.customer_id = o.customer_id
WHERE o.order_status IN ('completed', 'shipped')
GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment, c.city, c.state
ORDER BY lifetime_value DESC
LIMIT 20;

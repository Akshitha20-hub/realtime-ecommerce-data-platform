-- ============================================================
-- ANALYTICS QUERY 3: Top Products by Revenue
-- ============================================================
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity)                         AS total_units_sold,
    ROUND(SUM(oi.subtotal)::NUMERIC, 2)      AS total_revenue
FROM order_items oi
JOIN products    p  ON oi.product_id = p.product_id
JOIN orders      o  ON oi.order_id   = o.order_id
WHERE o.order_status IN ('completed', 'shipped')
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 20;

-- ============================================================
-- ANALYTICS QUERY 4: Revenue by Product Category
-- ============================================================
SELECT
    p.category,
    COUNT(DISTINCT o.order_id)              AS total_orders,
    SUM(oi.quantity)                        AS total_units_sold,
    ROUND(SUM(oi.subtotal)::NUMERIC, 2)     AS total_revenue,
    ROUND(AVG(p.product_rating)::NUMERIC, 2) AS avg_rating
FROM order_items oi
JOIN products p  ON oi.product_id = p.product_id
JOIN orders   o  ON oi.order_id   = o.order_id
WHERE o.order_status IN ('completed', 'shipped')
GROUP BY p.category
ORDER BY total_revenue DESC;

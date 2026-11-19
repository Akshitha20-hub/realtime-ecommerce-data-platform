-- ============================================================
-- ANALYTICS QUERY 6: Order Status Funnel
-- ============================================================
SELECT
    order_status,
    COUNT(*)                                        AS order_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_total,
    ROUND(SUM(total_amount)::NUMERIC, 2)            AS total_amount
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;

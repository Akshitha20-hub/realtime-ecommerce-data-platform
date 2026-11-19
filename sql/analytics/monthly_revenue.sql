-- ============================================================
-- ANALYTICS QUERY 2: Monthly Revenue Trend
-- ============================================================
SELECT
    EXTRACT(YEAR  FROM order_date)::INTEGER  AS order_year,
    EXTRACT(MONTH FROM order_date)::INTEGER  AS order_month,
    COUNT(DISTINCT order_id)                 AS total_orders,
    ROUND(SUM(total_amount)::NUMERIC, 2)     AS monthly_revenue
FROM orders
WHERE order_status IN ('completed', 'shipped')
GROUP BY order_year, order_month
ORDER BY order_year, order_month;

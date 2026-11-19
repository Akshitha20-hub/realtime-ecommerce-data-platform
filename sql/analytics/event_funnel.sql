-- ============================================================
-- ANALYTICS QUERY 8: Customer Event / Conversion Funnel
-- ============================================================
SELECT
    event_type,
    COUNT(*)                               AS event_count,
    COUNT(DISTINCT customer_id)            AS unique_customers
FROM events
GROUP BY event_type
ORDER BY event_count DESC;

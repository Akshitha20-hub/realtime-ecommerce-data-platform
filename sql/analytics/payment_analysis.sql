-- ============================================================
-- ANALYTICS QUERY 7: Payment Method Breakdown
-- ============================================================
SELECT
    payment_method,
    payment_status,
    COUNT(*)                               AS payment_count,
    ROUND(SUM(payment_amount)::NUMERIC, 2) AS total_amount
FROM payments
GROUP BY payment_method, payment_status
ORDER BY payment_method, payment_status;

SELECT
    tr_log.user_id,
    MAX(tr_log.user_email),
    COUNT(tr_log.log_data) AS total_log_data
FROM financial_analytics_log tr_log
WHERE tr_log.created_at > '@payment_created_at'
GROUP BY tr_log.user_id
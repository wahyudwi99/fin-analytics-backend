SELECT * FROM financial_analytics_log
WHERE user_email = '@email'
ORDER BY created_at DESC
LIMIT 1
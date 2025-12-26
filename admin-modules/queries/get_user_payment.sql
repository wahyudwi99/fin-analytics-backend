SELECT
    pay.user_id,
    pay.user_email,
    pay.amount,
    pay.total_balance,
    pay.balance_duration_days,
    pay.plan,
    pay.created_at
FROM financial_analytics_payment pay
WHERE pay.user_email = '@user_email'
    AND payment_status = 'Paid'
ORDER BY pay.created_at DESC
LIMIT 1
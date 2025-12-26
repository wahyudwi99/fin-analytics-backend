INSERT INTO financial_analytics_payment (
    user_id,
    user_email,
    amount,
    total_balance,
    balance_duration_days,
    plan,
    payment_status,
    payment_id,
    created_at
) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
UPDATE financial_analytics_payment
SET payment_status = '@PAYMENT_STATUS',
    updated_at = '@UPDATED_AT'
WHERE payment_id = '@PAYMENT_ID'
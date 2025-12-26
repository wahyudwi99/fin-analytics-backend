SELECT
    user_id,
    item_name,
    item_amount,
    item_value,
    created_at,
    CAST(TO_CHAR(created_at, 'DD') AS INTEGER) AS day_transaction,
    CASE
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 1 THEN 'Jan'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 2 THEN 'Feb'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 3 THEN 'Mar'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 4 THEN 'Apr'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 5 THEN 'May'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 6 THEN 'Jun'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 7 THEN 'Jul'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 8 THEN 'Aug'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 9 THEN 'Sep'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 10 THEN 'Oct'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 11 THEN 'Nov'
        WHEN CAST(TO_CHAR(created_at, 'MM') AS INTEGER) = 12 THEN 'Dec'
    END month_transaction
FROM financial_analytics_log
WHERE user_email
ORDER BY created_at ASC
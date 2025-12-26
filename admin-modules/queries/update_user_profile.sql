UPDATE financial_analytics_user_profile
SET name = '@name',
    email = '@email',
    phone_number = '@phone_number',
    address = '@address',
    updated_at = '@updated_at'
WHERE email = '@email'
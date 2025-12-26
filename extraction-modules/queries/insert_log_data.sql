INSERT INTO financial_analytics_log(
    user_id,
    user_email,
    log_data,
    input_token,
    output_token,
    created_at
)
VALUES(
    (SELECT id FROM financial_analytics_user_profile f_usr WHERE f_usr.email = %s),
    %s,
    %s,
    %s,
    %s,
    %s
)
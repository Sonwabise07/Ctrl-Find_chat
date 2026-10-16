    UNION ALL
    SELECT lc.asset_id, lc.reported_date, 'Reported ' || lower(lc.case_type),
           CASE WHEN lc.is_negligent THEN 'Negligent' ELSE 'Not negligent' END,
           COALESCE(lu.first_name || ' ' || lu.last_name, '-')
    FROM asset_management.loss_cases lc
    LEFT JOIN asset_management.users lu ON lu.user_id = lc.user_id

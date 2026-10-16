    UNION ALL
    SELECT c.asset_id, c.requested_date, 'Confirmation requested', y.name, '-'
    FROM asset_management.audit_confirmations c
    JOIN asset_management.audit_cycles y ON y.cycle_id = c.cycle_id
    UNION ALL
    SELECT c.asset_id, c.responded_date,
           CASE c.status WHEN 'Exception' THEN 'Exception reported' ELSE 'Confirmed' END,
           COALESCE(c.exception_reason, y.name), COALESCE(cu.first_name || ' ' || cu.last_name, '-')
    FROM asset_management.audit_confirmations c
    JOIN asset_management.audit_cycles y ON y.cycle_id = c.cycle_id
    LEFT JOIN asset_management.users cu ON cu.user_id = c.user_id
    WHERE c.responded_date IS NOT NULL

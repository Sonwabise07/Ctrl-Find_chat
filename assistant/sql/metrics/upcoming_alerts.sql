SELECT title, subtitle, tone FROM (
    SELECT 1 AS rank, r.reported_date AS due, r.issue AS title,
           'Open repair · ' || a.asset_no || ' · reported ' || to_char(r.reported_date, 'DD Mon') AS subtitle,
           'warn' AS tone
    FROM asset_management.maintenance_records r JOIN scoped a ON a.asset_id = r.asset_id
    WHERE r.status IN ('Open', 'In Progress')
    UNION ALL
    SELECT 2, a.warranty_expiry_date::timestamptz,
           'Warranty ends ' || to_char(a.warranty_expiry_date, 'DD Mon'),
           t.name || ' · ' || a.asset_no, 'info'
    FROM scoped a
    JOIN asset_management.asset_types t ON t.asset_type_id = a.asset_type_id
    JOIN asset_management.asset_statuses s ON s.status_id = a.status_id
    WHERE s.name NOT IN ('Retired', 'Lost')
      AND a.warranty_expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
) alerts
ORDER BY rank, due LIMIT 5

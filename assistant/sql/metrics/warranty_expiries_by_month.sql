SELECT to_char(m.month, 'Mon YY') AS label, COUNT(a.asset_id) AS value
FROM generate_series(date_trunc('month', CURRENT_DATE),
                     date_trunc('month', CURRENT_DATE) + interval '5 months', interval '1 month') AS m(month)
LEFT JOIN (SELECT sa.asset_id, sa.warranty_expiry_date FROM scoped sa
           JOIN asset_management.asset_statuses s ON s.status_id = sa.status_id
           WHERE s.name NOT IN ('Retired', 'Lost')) a
       ON a.warranty_expiry_date >= m.month AND a.warranty_expiry_date < m.month + interval '1 month'
GROUP BY m.month ORDER BY m.month

SELECT to_char(m.month, 'Mon YY') AS label, COALESCE(SUM(r.cost), 0) AS value
FROM generate_series(date_trunc('month', CURRENT_DATE) - interval '5 months',
                     date_trunc('month', CURRENT_DATE), interval '1 month') AS m(month)
LEFT JOIN (SELECT mr.cost, mr.reported_date FROM asset_management.maintenance_records mr
           JOIN scoped a ON a.asset_id = mr.asset_id) r
       ON r.reported_date >= m.month AND r.reported_date < m.month + interval '1 month'
GROUP BY m.month ORDER BY m.month

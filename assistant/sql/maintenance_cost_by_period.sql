SELECT m.label, COALESCE(SUM(r.cost), 0) AS value, COUNT(r.maintenance_id) AS items
FROM (VALUES (%(p1_label)s::text, %(p1_start)s::date, %(p1_end)s::date, 1),
             (%(p2_label)s::text, %(p2_start)s::date, %(p2_end)s::date, 2)) AS m(label, s, e, ord)
LEFT JOIN (SELECT mr.* FROM asset_management.maintenance_records mr JOIN scoped a ON a.asset_id = mr.asset_id) r
       ON r.reported_date >= m.s AND r.reported_date < m.e
GROUP BY m.label, m.ord ORDER BY m.ord

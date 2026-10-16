SELECT m.label, COALESCE(SUM(a.purchase_price), 0) AS value, COUNT(a.asset_id) AS items
FROM (VALUES (%(p1_label)s::text, %(p1_start)s::date, %(p1_end)s::date, 1),
             (%(p2_label)s::text, %(p2_start)s::date, %(p2_end)s::date, 2)) AS m(label, s, e, ord)
LEFT JOIN scoped a ON a.purchase_date >= m.s AND a.purchase_date < m.e
GROUP BY m.label, m.ord ORDER BY m.ord

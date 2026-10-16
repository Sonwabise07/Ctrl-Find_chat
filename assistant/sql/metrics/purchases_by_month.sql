SELECT to_char(m.month, 'Mon YY') AS label, COALESCE(SUM(a.purchase_price), 0) AS value
FROM generate_series(date_trunc('month', CURRENT_DATE) - interval '11 months',
                     date_trunc('month', CURRENT_DATE), interval '1 month') AS m(month)
LEFT JOIN scoped a ON a.purchase_date >= m.month AND a.purchase_date < m.month + interval '1 month'
GROUP BY m.month ORDER BY m.month

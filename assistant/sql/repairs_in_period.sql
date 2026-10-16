SELECT a.asset_no, r.issue, r.status, to_char(r.reported_date, 'DD Mon YYYY') AS reported,
       COALESCE(r.cost, 0) AS cost,
       COUNT(*) OVER () AS total, COALESCE(SUM(r.cost) OVER (), 0) AS total_cost
FROM scoped a {{JOINS}}
JOIN asset_management.maintenance_records r ON r.asset_id = a.asset_id
WHERE r.reported_date >= %(date_from)s::date AND r.reported_date < %(date_to)s::date + 1 AND {{FILTERS}}
ORDER BY r.reported_date DESC, a.asset_no LIMIT 25

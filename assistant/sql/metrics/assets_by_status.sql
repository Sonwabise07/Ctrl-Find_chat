SELECT s.name AS label, COUNT(*) AS value
FROM scoped a JOIN asset_management.asset_statuses s ON s.status_id = a.status_id
GROUP BY s.name ORDER BY value DESC, label

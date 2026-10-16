SELECT t.name AS label, COUNT(*) AS value
FROM scoped a
JOIN asset_management.asset_types t ON t.asset_type_id = a.asset_type_id
JOIN asset_management.asset_statuses s ON s.status_id = a.status_id
WHERE s.name = 'Available'
GROUP BY t.name ORDER BY value DESC, label

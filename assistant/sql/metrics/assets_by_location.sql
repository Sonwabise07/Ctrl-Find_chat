SELECT COALESCE(l.name, 'No location') AS label, COUNT(*) AS value
FROM scoped a LEFT JOIN asset_management.locations l ON l.location_id = a.location_id
GROUP BY 1 ORDER BY value DESC, label

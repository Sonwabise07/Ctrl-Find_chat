SELECT COUNT(*) FILTER (WHERE s.name = 'Assigned') AS value,
       COALESCE(ROUND(100.0 * COUNT(*) FILTER (WHERE s.name = 'Assigned') / NULLIF(COUNT(*), 0)), 0) || '%% of all assets' AS tag
FROM scoped a JOIN asset_management.asset_statuses s ON s.status_id = a.status_id

SELECT COUNT(*) AS value,
       COUNT(*) FILTER (WHERE r.status = 'In Progress') || ' in progress' AS tag
FROM asset_management.maintenance_records r JOIN scoped a ON a.asset_id = r.asset_id
WHERE r.status IN ('Open', 'In Progress')

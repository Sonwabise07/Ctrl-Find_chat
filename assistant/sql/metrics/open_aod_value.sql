SELECT COALESCE(SUM(r.amount), 0) AS value, COUNT(*) || ' open records' AS tag
FROM asset_management.aod_records r
JOIN scoped a ON a.asset_id = r.asset_id
WHERE r.status = 'Open'

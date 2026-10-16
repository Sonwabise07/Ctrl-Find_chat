SELECT COALESCE(l.name, 'No location') AS label, COUNT(*) AS value
FROM asset_management.audit_confirmations c
JOIN asset_management.audit_cycles y ON y.cycle_id = c.cycle_id AND y.status = 'Active'
JOIN scoped a ON a.asset_id = c.asset_id
LEFT JOIN asset_management.locations l ON l.location_id = a.location_id
WHERE c.status = 'Exception' GROUP BY 1 ORDER BY value DESC, label

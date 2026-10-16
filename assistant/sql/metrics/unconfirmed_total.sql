SELECT COUNT(*) AS value, COUNT(*) FILTER (WHERE c.due_date < CURRENT_DATE) || ' overdue' AS tag
FROM asset_management.audit_confirmations c
JOIN asset_management.audit_cycles y ON y.cycle_id = c.cycle_id AND y.status = 'Active'
JOIN scoped a ON a.asset_id = c.asset_id
WHERE c.status = 'Pending'

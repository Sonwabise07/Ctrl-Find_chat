SELECT a.asset_no, a.description, COALESCE(u.first_name || ' ' || u.last_name, '-') AS holder,
       to_char(c.due_date, 'DD Mon YYYY') AS due, COUNT(*) OVER () AS total
FROM asset_management.audit_confirmations c
JOIN asset_management.audit_cycles y ON y.cycle_id = c.cycle_id AND y.status = 'Active'
JOIN scoped a ON a.asset_id = c.asset_id
JOIN asset_management.asset_types t ON t.asset_type_id = a.asset_type_id
LEFT JOIN asset_management.users u ON u.user_id = c.user_id
WHERE c.status = 'Pending' AND (%(asset_type)s::text IS NULL OR t.name = %(asset_type)s)
ORDER BY c.due_date, a.asset_no LIMIT 25

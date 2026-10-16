SELECT COUNT(*) FILTER (WHERE a.warranty_expiry_date < CURRENT_DATE) AS value,
       COUNT(*) FILTER (WHERE a.warranty_expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 30) || ' end within 30 days' AS tag
FROM scoped a JOIN asset_management.asset_statuses s ON s.status_id = a.status_id
WHERE s.name NOT IN ('Retired', 'Lost')

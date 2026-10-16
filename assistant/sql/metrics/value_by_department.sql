SELECT COALESCE(d.name, 'No department') AS label, COALESCE(SUM(a.purchase_price), 0) AS value
FROM scoped a LEFT JOIN asset_management.departments d ON d.department_id = a.department_id
GROUP BY 1 ORDER BY value DESC, label

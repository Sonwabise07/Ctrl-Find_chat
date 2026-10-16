JOIN asset_management.asset_types t ON t.asset_type_id = a.asset_type_id
JOIN asset_management.asset_statuses s ON s.status_id = a.status_id
LEFT JOIN asset_management.locations l ON l.location_id = a.location_id
LEFT JOIN asset_management.departments d ON d.department_id = a.department_id
LEFT JOIN asset_management.users u ON u.user_id = a.assigned_to_user_id

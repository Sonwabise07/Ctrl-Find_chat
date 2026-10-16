SELECT a.asset_no || ' · ' || COALESCE(a.description, '') AS asset,
       h.action_type AS event,
       COALESCE(u.first_name || ' ' || u.last_name, '-') AS employee,
       to_char(h.changed_date, 'DD Mon YYYY') AS changed_on
FROM asset_management.asset_history h
JOIN scoped a ON a.asset_id = h.asset_id
LEFT JOIN asset_management.users u ON u.user_id = h.user_id
ORDER BY h.changed_date DESC, h.history_id DESC LIMIT 8

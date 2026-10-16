SELECT a.asset_no, a.description, s.name AS status, COALESCE(l.name, '-') AS location,
       COALESCE(to_char(a.warranty_expiry_date, 'DD Mon YYYY'), '-') AS warranty_end,
       COUNT(*) OVER () AS total
FROM scoped a {{JOINS}}
WHERE a.assigned_to_user_id = %(scope_user)s AND {{FILTERS}}
ORDER BY a.asset_no LIMIT 25

SELECT a.asset_no, a.description, s.name AS status, COALESCE(l.name, '-') AS location,
       COALESCE(u.first_name || ' ' || u.last_name, '-') AS assigned_to,
       COALESCE(d.name, '-') AS department, COUNT(*) OVER () AS total
FROM scoped a {{JOINS}}
WHERE a.department_id = %(user_department)s AND {{FILTERS}}
ORDER BY a.asset_no LIMIT 25

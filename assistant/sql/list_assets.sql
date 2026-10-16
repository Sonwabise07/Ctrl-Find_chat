SELECT a.asset_no, a.description, s.name AS status, COALESCE(l.name, '-') AS location,
       COALESCE(u.first_name || ' ' || u.last_name, '-') AS assigned_to, COUNT(*) OVER () AS total
FROM scoped a {{JOINS}} WHERE {{FILTERS}} ORDER BY a.asset_no LIMIT 25

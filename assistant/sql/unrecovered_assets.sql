SELECT a.asset_no, a.description, COALESCE(u.first_name || ' ' || u.last_name, '-') AS holder,
       s.name AS status, COALESCE(l.name, '-') AS location,
       COUNT(*) OVER () AS total,
       COUNT(*) FILTER (WHERE t.name = 'Laptop') OVER () AS laptops
FROM scoped a {{JOINS}}
WHERE u.is_active = false AND {{FILTERS}}
ORDER BY (t.name = 'Laptop') DESC, u.last_name, a.asset_no
LIMIT 25

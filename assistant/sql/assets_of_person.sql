SELECT a.asset_no, a.description, s.name AS status, COALESCE(l.name, '-') AS location,
       to_char(a.warranty_expiry_date, 'DD Mon YYYY') AS warranty_end, COUNT(*) OVER () AS total
FROM scoped a {{JOINS}} WHERE a.assigned_to_user_id = %(person_id)s ORDER BY a.asset_no LIMIT 25

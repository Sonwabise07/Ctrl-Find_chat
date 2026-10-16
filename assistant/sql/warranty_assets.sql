SELECT a.asset_no, a.description, COALESCE(l.name, '-') AS location,
       COALESCE(u.first_name || ' ' || u.last_name, '-') AS assigned_to,
       to_char(a.warranty_expiry_date, 'DD Mon YYYY') AS warranty_end, COUNT(*) OVER () AS total
FROM scoped a {{JOINS}}
WHERE a.warranty_expiry_date IS NOT NULL AND s.name NOT IN ('Retired', 'Lost')
  AND (%(date_from)s::date IS NULL OR a.warranty_expiry_date >= %(date_from)s::date)
  AND a.warranty_expiry_date <= %(date_to)s::date
  AND (%(asset_type)s::text IS NULL OR t.name = %(asset_type)s)
ORDER BY a.warranty_expiry_date, a.asset_no LIMIT 25

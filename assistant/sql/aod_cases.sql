SELECT a.asset_no, a.description, u.first_name || ' ' || u.last_name AS employee,
       r.amount, to_char(r.created_date, 'DD Mon YYYY') AS raised,
       COUNT(*) OVER () AS total, COALESCE(SUM(r.amount) OVER (), 0) AS total_amount
FROM asset_management.aod_records r
JOIN scoped a ON a.asset_id = r.asset_id
JOIN asset_management.users u ON u.user_id = r.user_id
WHERE r.status = 'Open'
ORDER BY r.amount DESC, a.asset_no
LIMIT 25

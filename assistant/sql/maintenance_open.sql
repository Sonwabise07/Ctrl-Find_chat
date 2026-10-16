SELECT a.asset_no, a.description, r.issue, r.status, to_char(r.reported_date, 'DD Mon YYYY') AS reported,
       COALESCE(sp.name, '-') AS supplier, COUNT(*) OVER () AS total
FROM asset_management.maintenance_records r JOIN scoped a ON a.asset_id = r.asset_id
LEFT JOIN asset_management.suppliers sp ON sp.supplier_id = r.supplier_id
WHERE r.status IN ('Open', 'In Progress') ORDER BY r.reported_date, a.asset_no LIMIT 25

SELECT 'Open AOD value' AS label, 'money' AS kind, COALESCE(SUM(r.amount), 0) AS value
FROM asset_management.aod_records r JOIN scoped a ON a.asset_id = r.asset_id WHERE r.status = 'Open'
UNION ALL
SELECT 'Open AOD records', 'count', COUNT(*)
FROM asset_management.aod_records r JOIN scoped a ON a.asset_id = r.asset_id WHERE r.status = 'Open'
UNION ALL
SELECT 'Purchase value of assets past warranty', 'money', COALESCE(SUM(a.purchase_price), 0)
FROM scoped a JOIN asset_management.asset_statuses s ON s.status_id = a.status_id
WHERE s.name NOT IN ('Retired', 'Lost') AND a.warranty_expiry_date < CURRENT_DATE

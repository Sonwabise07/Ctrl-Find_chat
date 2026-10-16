SELECT a.asset_no, a.description, c.case_type,
       CASE WHEN c.is_negligent THEN 'Negligent' ELSE 'Not negligent' END AS negligence,
       to_char(c.reported_date, 'DD Mon YYYY') AS reported,
       COALESCE(u.first_name || ' ' || u.last_name, '-') AS employee,
       COUNT(*) OVER () AS total,
       COUNT(*) FILTER (WHERE c.case_type = 'Lost') OVER () AS lost,
       COUNT(*) FILTER (WHERE c.case_type = 'Stolen') OVER () AS stolen,
       COUNT(*) FILTER (WHERE c.is_negligent) OVER () AS negligent
FROM asset_management.loss_cases c
JOIN scoped a ON a.asset_id = c.asset_id
LEFT JOIN asset_management.users u ON u.user_id = c.user_id
WHERE c.status = 'Open'
ORDER BY c.reported_date DESC, a.asset_no
LIMIT 25

-- Continues the `scoped` list that every query starts with.
, bounds AS (
    SELECT date_trunc('month', CURRENT_DATE) AS this_start,
           date_trunc('month', CURRENT_DATE) - interval '1 month' AS last_start
),
repairs AS (
    SELECT r.cost, r.reported_date FROM asset_management.maintenance_records r
    JOIN scoped a ON a.asset_id = r.asset_id
)
SELECT 'New assets registered' AS label, 'count' AS kind, 'good' AS up_is,
       COUNT(*) FILTER (WHERE a.created_date >= b.this_start) AS value,
       COUNT(*) FILTER (WHERE a.created_date >= b.last_start AND a.created_date < b.this_start) AS previous
FROM scoped a CROSS JOIN bounds b
UNION ALL
SELECT 'Purchase spend', 'money', 'neutral',
       COALESCE(SUM(a.purchase_price) FILTER (WHERE a.purchase_date >= b.this_start), 0),
       COALESCE(SUM(a.purchase_price) FILTER (WHERE a.purchase_date >= b.last_start AND a.purchase_date < b.this_start), 0)
FROM scoped a CROSS JOIN bounds b
UNION ALL
SELECT 'Repairs reported', 'count', 'bad',
       COUNT(*) FILTER (WHERE r.reported_date >= b.this_start),
       COUNT(*) FILTER (WHERE r.reported_date >= b.last_start AND r.reported_date < b.this_start)
FROM repairs r CROSS JOIN bounds b
UNION ALL
SELECT 'Repair cost', 'money', 'bad',
       COALESCE(SUM(r.cost) FILTER (WHERE r.reported_date >= b.this_start), 0),
       COALESCE(SUM(r.cost) FILTER (WHERE r.reported_date >= b.last_start AND r.reported_date < b.this_start), 0)
FROM repairs r CROSS JOIN bounds b

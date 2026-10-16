SELECT label, value FROM (
    SELECT CASE %(group_by)s WHEN 'status' THEN s.name WHEN 'type' THEN t.name
                             WHEN 'location' THEN l.name ELSE d.name END AS label,
           CASE %(rank_metric)s WHEN 'value' THEN COALESCE(SUM(a.purchase_price), 0) ELSE COUNT(*) END AS value
    FROM scoped a {{JOINS}} WHERE {{FILTERS}} GROUP BY 1
) ranked
WHERE label IS NOT NULL
ORDER BY CASE WHEN %(rank_order)s = 'asc' THEN value END ASC, value DESC, label
LIMIT %(rank_limit)s

SELECT CASE %(group_by)s WHEN 'status' THEN s.name WHEN 'type' THEN t.name
            WHEN 'location' THEN COALESCE(l.name, 'No location') ELSE COALESCE(d.name, 'No department') END AS label,
       COUNT(*) AS value, SUM(COUNT(*)) OVER () AS total
FROM scoped a {{JOINS}} WHERE {{FILTERS}} GROUP BY 1 ORDER BY value DESC, label

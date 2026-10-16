SELECT COUNT(*) AS value,
       '+' || COUNT(*) FILTER (WHERE a.created_date >= date_trunc('month', CURRENT_DATE)) || ' this month' AS tag
FROM scoped a

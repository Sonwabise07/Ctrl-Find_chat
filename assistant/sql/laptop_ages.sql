SELECT a.asset_no, COALESCE(u.first_name || ' ' || u.last_name, '-') AS holder,
       to_char(a.purchase_date, 'DD Mon YYYY') AS purchased,
       COALESCE(EXTRACT(YEAR FROM age(CURRENT_DATE, a.purchase_date))::int, 0) AS age_years,
       COALESCE(EXTRACT(MONTH FROM age(CURRENT_DATE, a.purchase_date))::int, 0) AS age_months,
       CASE WHEN a.warranty_expiry_date IS NULL THEN '-'
            WHEN a.warranty_expiry_date < CURRENT_DATE THEN 'Ended ' || to_char(a.warranty_expiry_date, 'DD Mon YYYY')
            ELSE 'Ends ' || to_char(a.warranty_expiry_date, 'DD Mon YYYY') END AS warranty,
       COUNT(*) OVER () AS total,
       COUNT(*) FILTER (WHERE a.warranty_expiry_date < CURRENT_DATE) OVER () AS past_warranty,
       COUNT(*) FILTER (WHERE a.warranty_expiry_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 90) OVER () AS ending_soon,
       90 AS soon_days
FROM scoped a {{JOINS}}
WHERE t.name = 'Laptop' AND s.name NOT IN ('Retired', 'Lost') AND {{FILTERS}}
ORDER BY a.purchase_date NULLS LAST, a.asset_no
LIMIT 25

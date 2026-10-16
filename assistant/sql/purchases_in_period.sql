SELECT a.asset_no, a.description, to_char(a.purchase_date, 'DD Mon YYYY') AS purchased,
       a.purchase_price AS price,
       COUNT(*) OVER () AS total, COALESCE(SUM(a.purchase_price) OVER (), 0) AS total_price
FROM scoped a {{JOINS}}
WHERE a.purchase_date >= %(date_from)s::date AND a.purchase_date <= %(date_to)s::date AND {{FILTERS}}
ORDER BY a.purchase_date DESC, a.asset_no LIMIT 25

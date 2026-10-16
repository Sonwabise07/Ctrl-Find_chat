-- Continues the `scoped` list that every query starts with.
, target AS (
    SELECT a.asset_id, a.asset_no FROM scoped a
    WHERE regexp_replace(upper(a.asset_no), '[^A-Z0-9]', '', 'g') = %(asset_ref)s
       OR regexp_replace(upper(COALESCE(a.serial_number, '')), '[^A-Z0-9]', '', 'g') = %(asset_ref)s
       OR regexp_replace(upper(COALESCE(a.tracking_no, '')), '[^A-Z0-9]', '', 'g') = %(asset_ref)s
    LIMIT 1
),
events AS (
    SELECT h.asset_id, h.changed_date AS occurred, h.action_type AS event,
           CASE WHEN h.old_value IS NOT NULL AND h.new_value IS NOT NULL THEN h.old_value || ' → ' || h.new_value
                ELSE COALESCE(h.new_value, h.old_value, '') END AS detail,
           COALESCE(hu.first_name || ' ' || hu.last_name, '-') AS done_by
    FROM asset_management.asset_history h
    LEFT JOIN asset_management.users hu ON hu.user_id = h.user_id
    UNION ALL
    SELECT r.asset_id, r.reported_date, 'Repair reported', r.issue, COALESCE(r.technician, '-')
    FROM asset_management.maintenance_records r
    UNION ALL
    SELECT r.asset_id, r.completion_date, 'Repair completed', r.issue, COALESCE(r.technician, '-')
    FROM asset_management.maintenance_records r WHERE r.completion_date IS NOT NULL
    {{EXTRA_EVENTS}}
)
SELECT t.asset_no, to_char(e.occurred, 'DD Mon YYYY') AS occurred, e.event, e.detail, e.done_by,
       COUNT(e.event) OVER () AS total
FROM target t LEFT JOIN events e ON e.asset_id = t.asset_id
ORDER BY e.occurred DESC NULLS LAST, e.event
LIMIT 40

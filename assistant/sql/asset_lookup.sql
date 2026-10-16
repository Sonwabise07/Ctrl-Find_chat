SELECT a.asset_no, a.description, s.name AS status,
       COALESCE(l.name, '-') AS location, COALESCE(d.name, '-') AS department,
       COALESCE(u.first_name || ' ' || u.last_name, '-') AS holder,
       COALESCE(a.serial_number, '-') AS serial_number,
       to_char(a.purchase_date, 'DD Mon YYYY') AS purchased, a.purchase_price,
       to_char(a.warranty_expiry_date, 'DD Mon YYYY') AS warranty_end,
       COALESCE(a.warranty_expiry_date < CURRENT_DATE, false) AS warranty_ended,
       (SELECT COUNT(*) FROM asset_management.maintenance_records r WHERE r.asset_id = a.asset_id) AS repairs,
       (SELECT COUNT(*) FROM asset_management.maintenance_records r
         WHERE r.asset_id = a.asset_id AND r.status IN ('Open', 'In Progress')) AS open_repairs,
       (SELECT COALESCE(SUM(r.cost), 0) FROM asset_management.maintenance_records r
         WHERE r.asset_id = a.asset_id) AS repair_cost,
       (SELECT COALESCE(json_agg(json_build_object('changed_on', e.changed_on, 'event', e.event,
                                                   'employee', e.employee) ORDER BY e.sort DESC, e.id DESC), '[]'::json)
          FROM (SELECT h.changed_date AS sort, h.history_id AS id,
                       to_char(h.changed_date, 'DD Mon YYYY') AS changed_on, h.action_type AS event,
                       COALESCE(hu.first_name || ' ' || hu.last_name, '-') AS employee
                FROM asset_management.asset_history h
                LEFT JOIN asset_management.users hu ON hu.user_id = h.user_id
                WHERE h.asset_id = a.asset_id
                ORDER BY h.changed_date DESC, h.history_id DESC LIMIT 5) e) AS history
FROM scoped a
JOIN asset_management.asset_statuses s ON s.status_id = a.status_id
LEFT JOIN asset_management.locations l ON l.location_id = a.location_id
LEFT JOIN asset_management.departments d ON d.department_id = a.department_id
LEFT JOIN asset_management.users u ON u.user_id = a.assigned_to_user_id
WHERE regexp_replace(upper(a.asset_no), '[^A-Z0-9]', '', 'g') = %(asset_ref)s
   OR regexp_replace(upper(COALESCE(a.serial_number, '')), '[^A-Z0-9]', '', 'g') = %(asset_ref)s
   OR regexp_replace(upper(COALESCE(a.tracking_no, '')), '[^A-Z0-9]', '', 'g') = %(asset_ref)s
LIMIT 1

-- Dummy data for the PROPOSED tables (testing only). Run after proposed_migration.sql.
BEGIN;
INSERT INTO asset_management.audit_cycles (name, start_date, end_date) VALUES ('Self-confirmation cycle', CURRENT_DATE - 20, CURRENT_DATE + 10);
-- every assigned asset gets a request; outcome rotates so every status exists (some pending ones are overdue)
INSERT INTO asset_management.audit_confirmations (cycle_id, asset_id, user_id, requested_date, due_date, responded_date, status, exception_reason)
SELECT 1, asset_id, assigned_to_user_id, CURRENT_TIMESTAMP - interval '20 days',
       CASE WHEN rn % 5 = 3 THEN CURRENT_DATE - 5 ELSE CURRENT_DATE + 7 END,
       CASE WHEN rn % 5 IN (0, 1, 4) THEN CURRENT_TIMESTAMP - interval '3 days' END,
       CASE rn % 5 WHEN 0 THEN 'Confirmed' WHEN 1 THEN 'Confirmed' WHEN 4 THEN 'Exception' ELSE 'Pending' END,
       CASE WHEN rn % 5 = 4 THEN 'Asset not at recorded location' END
FROM (SELECT asset_id, assigned_to_user_id, row_number() OVER (ORDER BY asset_id) AS rn
      FROM asset_management.assets WHERE assigned_to_user_id IS NOT NULL) x;
-- cases on the two Lost assets and one Retired laptop
INSERT INTO asset_management.loss_cases (asset_id, user_id, case_type, is_negligent, status)
SELECT asset_id, (asset_id % 10) + 1, CASE WHEN status_id = 4 THEN 'Stolen' ELSE 'Lost' END, status_id <> 4 OR asset_id % 2 = 1, CASE WHEN status_id = 4 THEN 'Closed' ELSE 'Open' END
FROM asset_management.assets WHERE status_id IN (4, 5) AND asset_type_id IN (1, 4, 5);
INSERT INTO asset_management.aod_records (case_id, asset_id, user_id, amount, status)
SELECT c.case_id, c.asset_id, c.user_id, a.purchase_price, CASE WHEN c.status = 'Closed' THEN 'Recovered' ELSE 'Open' END
FROM asset_management.loss_cases c JOIN asset_management.assets a USING (asset_id) WHERE c.is_negligent;
COMMIT;

"""Every expected figure comes from an independent SQL query, never from the assistant itself."""

S = "asset_management."


def bold(reply: dict, index: int = 1) -> str:
    """The text between the Nth pair of ** markers in the answer."""
    return reply["answer"].split("**")[index]


def count_in(reply: dict, index: int = 1) -> int:
    return int(bold(reply, index).split()[0])


def test_count_by_type_and_status(api, sql):
    reply = api.ask("How many laptops are available?")
    expected = sql(f"SELECT count(*) FROM {S}assets WHERE asset_type_id = 1 AND status_id = 1")[0][0]
    assert count_in(reply) == expected


def test_make_is_matched_on_description(api, sql):
    reply = api.ask("How many MacBooks do we have?")
    expected = sql(f"SELECT count(*) FROM {S}assets WHERE description ILIKE 'MacBook%'")[0][0]
    assert count_in(reply) == expected
    assert "description" in reply["source"]


def test_breakdown_adds_up_to_all_assets(api, sql):
    reply = api.ask("Show assets by status")
    total = sql(f"SELECT count(*) FROM {S}assets")[0][0]
    assert count_in(reply) == total
    assert sum(row["value"] for row in reply["chart"]["rows"]) == total


def test_warranty_next_month(api, sql):
    reply = api.ask("Which assets go out of warranty next month?")
    expected = sql(
        f"""SELECT count(*) FROM {S}assets
            WHERE status_id NOT IN (4, 5)
              AND warranty_expiry_date >= date_trunc('month', current_date + interval '1 month')
              AND warranty_expiry_date <  date_trunc('month', current_date + interval '2 month')"""
    )[0][0]
    assert count_in(reply) == expected == len(reply["table"]["rows"])


def test_already_out_of_warranty(api, sql):
    reply = api.ask("Show assets already out of warranty")
    expected = sql(
        f"""SELECT count(*) FROM {S}assets
            WHERE status_id NOT IN (4, 5) AND warranty_expiry_date < current_date"""
    )[0][0]
    assert count_in(reply) == expected


def test_purchase_spend_comparison(api, sql):
    reply = api.ask("Compare purchase spend this month and last month")
    expected = [
        float(row[0])
        for row in sql(
            f"""SELECT coalesce(sum(a.purchase_price), 0)
                FROM (SELECT date_trunc('month', current_date - interval '1 month') AS s,
                             date_trunc('month', current_date) AS e
                      UNION ALL
                      SELECT date_trunc('month', current_date),
                             date_trunc('month', current_date + interval '1 month')) p
                LEFT JOIN {S}assets a ON a.purchase_date >= p.s AND a.purchase_date < p.e
                GROUP BY p.s ORDER BY p.s"""
        )
    ]
    assert [row["value"] for row in reply["chart"]["rows"]] == expected


def test_repair_cost_comparison_by_quarter(api):
    reply = api.ask("Compare repair costs this quarter and last quarter")
    assert reply["scope"] == "in"
    assert len(reply["chart"]["rows"]) == 2


def test_unconfirmed_laptops(api, sql):
    reply = api.ask("How many laptops are currently unconfirmed?")
    expected = sql(
        f"""SELECT count(*) FROM {S}audit_confirmations c JOIN {S}assets a USING (asset_id)
            WHERE c.status = 'Pending' AND a.asset_type_id = 1"""
    )[0][0]
    assert count_in(reply) == expected


def test_overdue_confirmations(api, sql):
    reply = api.ask("Which confirmations are overdue?")
    expected = sql(
        f"SELECT count(*) FROM {S}audit_confirmations WHERE status = 'Pending' AND due_date < current_date"
    )[0][0]
    assert count_in(reply) == expected


def test_office_with_most_audit_exceptions(api, sql):
    reply = api.ask("Which office has the most audit exceptions?")
    name, count = sql(
        f"""SELECT l.name, count(*) FROM {S}audit_confirmations c
            JOIN {S}assets a USING (asset_id) JOIN {S}locations l USING (location_id)
            WHERE c.status = 'Exception' GROUP BY 1 ORDER BY 2 DESC LIMIT 1"""
    )[0]
    assert name in reply["answer"]
    assert reply["chart"]["rows"][0]["value"] == count


def test_open_aod_value(api, sql):
    reply = api.ask("What is the open AOD value?")
    expected = float(sql(f"SELECT sum(amount) FROM {S}aod_records WHERE status = 'Open'")[0][0])
    shown = bold(reply, 1).replace("R", "").replace("\u202f", "")
    assert float(shown) == expected


def test_open_repair_cases(api, sql):
    reply = api.ask("Show open repair cases")
    expected = sql(f"SELECT count(*) FROM {S}maintenance_records WHERE status IN ('Open', 'In Progress')")[0][
        0
    ]
    assert count_in(reply) == expected


def test_assets_held_by_a_person(api, sql):
    reply = api.ask("What does Thandi Nkosi have?")
    expected = sql(
        f"""SELECT count(*) FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
            WHERE u.first_name = 'Thandi'"""
    )[0][0]
    assert count_in(reply, 3) == expected


def test_follow_up_keeps_the_question_type(api):
    first = api.ask("How many monitors are available?")
    reply = api.ask("and laptops?", {"intent": first["intent"], "slots": first["slots"]})
    assert reply["intent"] == "count_assets"
    assert reply["slots"]["asset_type"] == "Laptop"
    assert reply["slots"]["status"] == "Available"

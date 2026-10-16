"""Your assets, asset history, leavers, loss and AOD cases, and laptop age. Expected values come from SQL."""

import pytest

from assistant.app import build_service
from assistant.data.lookups import table_inventory
from assistant.identity import CurrentUser

S = "asset_management."
EMPLOYEE = "thandi.nkosi@example.co.za"
MANAGER = "sipho.dlamini@example.co.za"
NOBODY = "nobody@example.co.za"


def bold(reply: dict, index: int = 1) -> str:
    return reply["answer"].split("**")[index]


def first_number(reply: dict, index: int = 1) -> int:
    return int(bold(reply, index).split()[0])


# ---- my assets and my team


def test_my_assets_are_only_those_assigned_to_me_whatever_my_role(api, sql):
    for email, first_name in ((None, "Naledi"), (EMPLOYEE, "Thandi"), (MANAGER, "Sipho")):
        mine = sql(
            f"""SELECT count(*) FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
                WHERE u.first_name = %s""",
            first_name,
        )[0][0]
        reply = api.ask("What am I responsible for?", email=email)
        assert (reply["intent"], first_number(reply)) == ("my_assets", mine)


def test_my_laptops_apply_the_type_filter(api, sql):
    mine = sql(
        f"""SELECT count(*) FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
            WHERE u.first_name = 'Thandi' AND a.asset_type_id = 1"""
    )[0][0]
    assert first_number(api.ask("Show my laptops", email=EMPLOYEE)) == mine


def test_a_manager_sees_the_whole_department_as_their_team(api, sql):
    expected = sql(
        f"""SELECT count(*) FROM {S}assets
            WHERE department_id = (SELECT department_id FROM {S}users WHERE first_name = 'Sipho')"""
    )[0][0]
    reply = api.ask("Show my team's assets", email=MANAGER)
    assert (reply["intent"], first_number(reply)) == ("team_assets", expected)
    assert "no manager link" in reply["source"]


def test_an_employee_sees_only_their_own_assets_in_their_team(api, sql):
    expected = sql(
        f"""SELECT count(*) FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
            WHERE u.first_name = 'Thandi' AND a.department_id = u.department_id"""
    )[0][0]
    assert first_number(api.ask("What does my department have?", email=EMPLOYEE)) == expected


def test_someone_with_no_known_team_is_told_so(api):
    reply = api.ask("Show my team's assets", email=NOBODY)
    assert reply["scope"] == "out"
    assert "can't tell which team" in reply["answer"]


# ---- asset history


def history_count(sql, asset_no: str) -> int:
    """Every kind of event recorded for the asset, counted straight from the tables."""
    for_asset = f"JOIN {S}assets a USING (asset_id) WHERE a.asset_no = %s"
    counts = [
        f"SELECT count(*) FROM {S}asset_history h {for_asset}",
        f"SELECT count(*) FROM {S}maintenance_records r {for_asset}",
        f"SELECT count(*) FROM {S}maintenance_records r {for_asset} AND r.completion_date IS NOT NULL",
        f"SELECT count(*) FROM {S}audit_confirmations c {for_asset}",
        f"SELECT count(*) FROM {S}audit_confirmations c {for_asset} AND c.responded_date IS NOT NULL",
        f"SELECT count(*) FROM {S}loss_cases c {for_asset}",
    ]
    return sum(sql(query, asset_no)[0][0] for query in counts)


@pytest.mark.parametrize("asset_no", ["AST-0001", "AST-0013", "AST-0037"])
def test_the_history_merges_every_source_for_an_asset(api, sql, asset_no):
    reply = api.ask(f"Show the history of {asset_no}")
    expected = history_count(sql, asset_no)
    assert reply["intent"] == "asset_timeline"
    assert first_number(reply, 3) == expected
    assert len(reply["table"]["rows"]) == min(expected, 40)


def test_the_history_is_newest_first(api, sql):
    for_asset = f"JOIN {S}assets a USING (asset_id) WHERE a.asset_no = 'AST-0001'"
    latest = sql(
        f"""SELECT to_char(max(d), 'DD Mon YYYY') FROM (
              SELECT h.changed_date AS d FROM {S}asset_history h {for_asset}
              UNION ALL
              SELECT c.responded_date FROM {S}audit_confirmations c {for_asset}) x"""
    )[0][0]
    assert api.ask("Show the history of AST-0001")["table"]["rows"][0]["occurred"] == latest


def test_an_asset_card_offers_its_history_and_the_follow_up_works(api):
    card = api.ask("Tell me about AST-0001")
    assert [chip["label"] for chip in card["chips"]] == ["Full history"]
    from_chip = api.ask(card["chips"][0]["question"])
    by_follow_up = api.ask("show its history", {"intent": card["intent"], "slots": card["slots"]})
    assert from_chip["intent"] == by_follow_up["intent"] == "asset_timeline"
    assert from_chip["answer"] == by_follow_up["answer"]


def test_the_history_of_an_unknown_asset_is_not_guessed(api):
    reply = api.ask("Show the history of AST-9999")
    assert "couldn't find" in reply["answer"]
    assert reply["table"] is None


def test_history_still_works_without_the_audit_and_loss_tables(settings):
    service = build_service(settings)
    user = CurrentUser(id=3, name="Naledi Mokoena", role="fixed_assets", department_id=5)
    with service.database.cursor() as cursor:
        everything = frozenset(table_inventory(cursor, service.catalog))
        cursor.execute(
            f"SELECT a.asset_no FROM {S}assets a JOIN {S}audit_confirmations c USING (asset_id) LIMIT 1"
        )
        slots = {"asset_ref": "".join(ch for ch in cursor.fetchone()["asset_no"] if ch.isalnum()).upper()}
        full = service.runner.run(cursor, "asset_timeline", slots, user, tables=everything).rows[0]["total"]
        core = service.runner.run(cursor, "asset_timeline", slots, user, tables=frozenset()).rows[0]["total"]
    assert full > core > 0


# ---- people who left


def test_assets_still_held_by_people_who_are_no_longer_active(api, sql):
    held, laptops = sql(
        f"""SELECT count(*), count(*) FILTER (WHERE a.asset_type_id = 1)
            FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id WHERE NOT u.is_active"""
    )[0]
    reply = api.ask("Which assets are still held by people who have left?")
    assert (reply["intent"], first_number(reply)) == ("unrecovered_assets", held)
    assert first_number(reply, 3) == laptops
    assert "no exit dates" in reply["source"]
    assert (
        "Laptop" in reply["table"]["rows"][0]["description"]
        or "laptop" in reply["table"]["rows"][0]["description"]
    )


def test_an_employee_does_not_see_other_peoples_leavers(api):
    reply = api.ask("Which assets are still held by people who have left?", email=EMPLOYEE)
    assert reply["table"] is None
    assert reply["answer"].startswith("No assets")


# ---- loss, theft and AOD


def test_open_loss_and_theft_cases(api, sql):
    total, lost, stolen, negligent = sql(
        f"""SELECT count(*), count(*) FILTER (WHERE case_type = 'Lost'),
                   count(*) FILTER (WHERE case_type = 'Stolen'), count(*) FILTER (WHERE is_negligent)
            FROM {S}loss_cases WHERE status = 'Open'"""
    )[0]
    reply = api.ask("Show open loss and theft cases")
    assert reply["intent"] == "open_loss_cases"
    assert [first_number(reply, i) for i in (1, 3, 5, 7)] == [total, lost, stolen, negligent]
    assert len(reply["table"]["rows"]) == total


def test_open_aod_cases_name_who_owes_what(api, sql):
    total, amount = sql(f"SELECT count(*), sum(amount) FROM {S}aod_records WHERE status = 'Open'")[0]
    reply = api.ask("Who has an open AOD?")
    assert reply["intent"] == "aod_cases"
    assert first_number(reply) == total
    assert float(bold(reply, 3).replace("R", "").replace("\u202f", "")) == float(amount)
    assert all(row["amount"].startswith("R") for row in reply["table"]["rows"])


def test_the_aod_value_question_is_unchanged(api):
    assert api.ask("What is the open AOD value?")["intent"] == "open_aod_value"


# ---- laptop age and warranty


def test_laptop_ages_and_warranty(api, sql):
    total, past, soon = sql(
        f"""SELECT count(*), count(*) FILTER (WHERE warranty_expiry_date < current_date),
                   count(*) FILTER (WHERE warranty_expiry_date BETWEEN current_date AND current_date + 90)
            FROM {S}assets WHERE asset_type_id = 1 AND status_id NOT IN (4, 5)"""
    )[0]
    reply = api.ask("How old are our laptops?")
    assert (reply["intent"], first_number(reply), first_number(reply, 3), first_number(reply, 5)) == (
        "laptop_ages",
        total,
        past,
        soon,
    )
    oldest = sql(
        f"""SELECT asset_no FROM {S}assets WHERE asset_type_id = 1 AND status_id NOT IN (4, 5)
            ORDER BY purchase_date, asset_no LIMIT 1"""
    )[0][0]
    assert reply["table"]["rows"][0]["asset_no"] == oldest
    assert "year" in reply["table"]["rows"][0]["age"] or "month" in reply["table"]["rows"][0]["age"]


def test_spare_stock_by_location_splits_by_location(api, sql):
    expected = sql(f"SELECT count(*) FROM {S}assets WHERE status_id = 1")[0][0]
    reply = api.ask("Show spare stock by location")
    assert reply["slots"]["group_by"] == "location"
    assert sum(row["value"] for row in reply["chart"]["rows"]) == expected

"""Asset lookup, rankings, date ranges and asset age. Expected values come from separate SQL."""

from datetime import date

import pytest

S = "asset_management."
EMPLOYEE = "thandi.nkosi@example.co.za"


def bold(reply: dict, index: int = 1) -> str:
    return reply["answer"].split("**")[index]


def count_in(reply: dict) -> int:
    return int(bold(reply).split()[0])


def money_in(reply: dict, index: int) -> float:
    return float(bold(reply, index).replace("R", "").replace("\u202f", ""))


# ---- asset lookup


def test_an_asset_card_shows_the_facts_and_recent_history(api, sql):
    reply = api.ask("Tell me about AST-0013")
    status, location, serial, repairs = sql(
        f"""SELECT s.name, l.name, a.serial_number,
                   (SELECT count(*) FROM {S}maintenance_records r WHERE r.asset_id = a.asset_id)
            FROM {S}assets a
            JOIN {S}asset_statuses s USING (status_id)
            LEFT JOIN {S}locations l USING (location_id)
            WHERE a.asset_no = 'AST-0013'"""
    )[0]
    events = sql(
        f"""SELECT count(*) FROM {S}asset_history h JOIN {S}assets a USING (asset_id)
            WHERE a.asset_no = 'AST-0013'"""
    )[0][0]
    card = {row["label"]: row["text"] for row in reply["details"]["rows"]}
    assert (reply["intent"], reply["details"]["title"]) == ("asset_lookup", "AST-0013")
    assert (card["Status"], card["Location"], card["Serial number"]) == (status, location, serial)
    assert card["Repairs"].startswith(f"{repairs} repair")
    assert len(reply["table"]["rows"]) == min(5, events)


@pytest.mark.parametrize("question", ["ast0013", "Where is AST-0013?", "who has ast-0013"])
def test_an_asset_number_is_found_however_it_is_typed(api, question):
    assert api.ask(question)["details"]["title"] == "AST-0013"


def test_an_asset_can_be_found_by_serial_number(api, sql):
    asset_no, serial = sql(
        f"SELECT asset_no, serial_number FROM {S}assets WHERE serial_number IS NOT NULL LIMIT 1"
    )[0]
    assert api.ask(f"serial number {serial}")["details"]["title"] == asset_no


def test_an_unknown_asset_number_is_not_guessed(api):
    reply = api.ask("details for AST-9999")
    assert reply["scope"] == "in"
    assert "couldn't find" in reply["answer"]
    assert reply["details"] is None


def test_an_employee_can_only_look_up_their_own_assets(api, sql):
    own = sql(
        f"""SELECT a.asset_no FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
            WHERE u.first_name = 'Thandi' LIMIT 1"""
    )[0][0]
    other = sql(
        f"""SELECT a.asset_no FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
            WHERE u.first_name <> 'Thandi' LIMIT 1"""
    )[0][0]
    assert api.ask(f"Tell me about {own}", email=EMPLOYEE)["details"]["title"] == own
    assert api.ask(f"Tell me about {other}", email=EMPLOYEE)["details"] is None


# ---- rankings


def test_the_location_with_the_most_laptops(api, sql):
    rows = sql(
        f"""SELECT l.name, count(*) FROM {S}assets a JOIN {S}locations l USING (location_id)
            WHERE a.asset_type_id = 1 GROUP BY 1 ORDER BY 2 DESC, 1"""
    )
    reply = api.ask("Which location has the most laptops?")
    assert reply["intent"] == "ranking"
    assert [(r["label"], r["value"]) for r in reply["chart"]["rows"]] == rows
    assert bold(reply) == rows[0][0]


def test_the_location_with_the_fewest_laptops(api, sql):
    rows = sql(
        f"""SELECT l.name, count(*) FROM {S}assets a JOIN {S}locations l USING (location_id)
            WHERE a.asset_type_id = 1 GROUP BY 1 ORDER BY 2, 1"""
    )
    reply = api.ask("Which location has the fewest laptops?")
    assert [(r["label"], r["value"]) for r in reply["chart"]["rows"]] == rows
    assert "the fewest" in reply["answer"]


def test_top_departments_by_value_respects_the_limit_and_leaves_out_no_department(api, sql):
    rows = sql(
        f"""SELECT d.name, sum(a.purchase_price) FROM {S}assets a JOIN {S}departments d USING (department_id)
            GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 3"""
    )
    reply = api.ask("Top 3 departments by asset value")
    assert [(r["label"], r["value"]) for r in reply["chart"]["rows"]] == [(n, float(v)) for n, v in rows]
    assert money_in(reply, 3) == float(rows[0][1])


def test_a_ranking_never_includes_assets_without_the_group(api):
    labels = [r["label"] for r in api.ask("Which department has the most assets?")["chart"]["rows"]]
    assert "No department" not in labels


def test_asset_type_by_value(api, sql):
    top = sql(
        f"""SELECT t.name FROM {S}assets a JOIN {S}asset_types t USING (asset_type_id)
            GROUP BY 1 ORDER BY sum(a.purchase_price) DESC LIMIT 1"""
    )[0][0]
    assert bold(api.ask("Which asset type is the most expensive?")) == top


# ---- date ranges


def test_purchases_in_the_last_90_days(api, sql):
    count, total = sql(
        f"""SELECT count(*), coalesce(sum(purchase_price), 0) FROM {S}assets
            WHERE purchase_date >= current_date - 90 AND purchase_date <= current_date"""
    )[0]
    reply = api.ask("What did we buy in the last 90 days?")
    assert reply["intent"] == "purchases_in_period"
    assert count_in(reply) == count
    assert money_in(reply, 3) == float(total)
    assert len(reply["table"]["rows"]) == min(count, 25)


def test_repairs_in_the_last_30_days(api, sql):
    count, cost = sql(
        f"""SELECT count(*), coalesce(sum(cost), 0) FROM {S}maintenance_records
            WHERE reported_date >= current_date - 30 AND reported_date < current_date + 1"""
    )[0]
    reply = api.ask("How many repairs were reported in the last 30 days?")
    assert reply["intent"] == "repairs_in_period"
    assert int(bold(reply).split()[0]) == count
    assert money_in(reply, 3) == float(cost)


def test_purchases_between_two_months(api, sql):
    today = date.today()
    year = today.year - (today.month < 7)
    count = sql(
        f"""SELECT count(*) FROM {S}assets
            WHERE purchase_date >= %s AND purchase_date <= %s""",
        date(year, 7, 1),
        date(year, 9, 30),
    )[0][0]
    reply = api.ask("Which assets were bought between July and September?")
    assert (reply["intent"], reply["slots"]["date_from"]) == (
        "purchases_in_period",
        date(year, 7, 1).isoformat(),
    )
    assert count_in(reply) == count


def test_a_period_can_be_narrowed_by_type_and_carried_into_a_follow_up(api, sql):
    first = api.ask("What did we buy in the last 90 days?")
    reply = api.ask("and monitors?", {"intent": first["intent"], "slots": first["slots"]})
    expected = sql(
        f"""SELECT count(*) FROM {S}assets WHERE asset_type_id = 3
            AND purchase_date >= current_date - 90 AND purchase_date <= current_date"""
    )[0][0]
    assert reply["intent"] == "purchases_in_period"
    assert count_in(reply) == expected


@pytest.mark.parametrize(
    "question",
    ["How many assets were added this month?", "Which location has the most laptops bought this year?"],
)
def test_a_date_on_a_question_that_cannot_use_one_is_refused_not_ignored(api, question):
    reply = api.ask(question)
    assert reply["scope"] == "out"
    assert "can't filter that by date" in reply["answer"]


# ---- asset age


def test_laptops_older_than_a_year(api, sql):
    expected = sql(
        f"""SELECT count(*) FROM {S}assets WHERE asset_type_id = 1
            AND purchase_date <= current_date - interval '12 months'"""
    )[0][0]
    reply = api.ask("How many laptops are older than 1 year?")
    assert count_in(reply) == expected
    assert reply["answer"].endswith("older than 1 year.")


def test_older_than_applies_to_lists_and_rankings_too(api, sql):
    expected = sql(
        f"""SELECT count(*) FROM {S}assets WHERE asset_type_id = 3
            AND purchase_date <= current_date - interval '24 months'"""
    )[0][0]
    assert count_in(api.ask("List monitors older than 2 years")) == expected
    assert (
        "older than 1 year" in api.ask("Which department has the most laptops older than 1 year?")["answer"]
    )

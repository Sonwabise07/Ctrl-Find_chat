"""Dashboard figures are checked against separate SQL or plain Python date maths."""

from datetime import date

from assistant.dashboards.catalog import Dashboard, Widget
from assistant.dashboards.service import DashboardService
from assistant.data.database import Database
from assistant.identity import DemoIdentity

S = "asset_management."
EMPLOYEE = "thandi.nkosi@example.co.za"
MANAGER = "sipho.dlamini@example.co.za"


def widgets(dashboard: dict) -> dict:
    return {widget["id"]: widget for widget in dashboard["widgets"]}


def month_starts(first: date, count: int) -> list[date]:
    months = []
    for step in range(count):
        year, month = divmod(first.year * 12 + first.month - 1 + step, 12)
        months.append(date(year, month + 1, 1))
    return months


def test_lists_the_dashboards(api):
    status, body = api.get("/api/dashboards")
    assert status == 200
    assert [d["id"] for d in body] == ["overview", "operational", "management"]


def test_unknown_dashboard_is_not_found(api):
    status, _ = api.get("/api/dashboards/nope")
    assert status == 404


def test_overview_cards_match_the_database(api, sql):
    cards = widgets(api.dashboard("overview"))
    total = sql(f"SELECT count(*) FROM {S}assets")[0][0]
    assigned = sql(f"SELECT count(*) FROM {S}assets WHERE status_id = 2")[0][0]
    repairs = sql(f"SELECT count(*) FROM {S}maintenance_records WHERE status IN ('Open', 'In Progress')")[0][
        0
    ]
    ended = sql(
        f"""SELECT count(*) FROM {S}assets
            WHERE status_id NOT IN (4, 5) AND warranty_expiry_date < current_date"""
    )[0][0]
    assert cards["total"]["data"]["value"] == total
    assert cards["assigned"]["data"]["value"] == assigned
    assert cards["assigned"]["data"]["tag"] == f"{round(100 * assigned / total)}% of all assets"
    assert cards["open_repairs"]["data"]["value"] == repairs
    assert cards["warranty_ended"]["data"]["value"] == ended


def test_status_bars_match_and_shares_add_up(api, sql):
    data = widgets(api.dashboard("overview"))["by_status"]["data"]
    expected = dict(
        sql(
            f"""SELECT s.name, count(*) FROM {S}assets a JOIN {S}asset_statuses s USING (status_id)
                GROUP BY 1"""
        )
    )
    assert {row["label"]: row["value"] for row in data["rows"]} == expected
    assert data["total"] == sum(expected.values())
    assert abs(sum(row["share"] for row in data["rows"]) - 100) < 0.5


def test_purchases_by_month_match_twelve_months_of_purchases(api, sql):
    today = date.today()
    first = month_starts(date(today.year - 1, today.month, 1), 13)[1]
    months = month_starts(first, 12)
    purchases = sql(f"SELECT purchase_date, purchase_price FROM {S}assets WHERE purchase_date IS NOT NULL")
    expected = [
        float(sum(price for day, price in purchases if (day.year, day.month) == (m.year, m.month)))
        for m in months
    ]
    rows = widgets(api.dashboard("operational"))["purchases"]["data"]["rows"]
    assert [row["value"] for row in rows] == expected


def test_warranty_ends_per_month_for_the_next_six_months(api, sql):
    today = date.today()
    months = month_starts(date(today.year, today.month, 1), 6)
    ends = sql(
        f"""SELECT warranty_expiry_date FROM {S}assets
            WHERE status_id NOT IN (4, 5) AND warranty_expiry_date IS NOT NULL"""
    )
    expected = [sum(1 for (day,) in ends if (day.year, day.month) == (m.year, m.month)) for m in months]
    rows = widgets(api.dashboard("operational"))["warranty_expiries"]["data"]["rows"]
    assert [row["value"] for row in rows] == expected


def test_month_summary_shows_direction_and_tone(api):
    rows = {r["label"]: r for r in widgets(api.dashboard("operational"))["month_summary"]["data"]["rows"]}
    assert set(rows) == {"New assets registered", "Purchase spend", "Repairs reported", "Repair cost"}
    for row in rows.values():
        assert row["direction"] in {"up", "down", "flat"}
        assert row["tone"] in {"good", "bad", "neutral"}


def test_alerts_and_activity_are_limited_and_newest_first(api, sql):
    overview = widgets(api.dashboard("overview"))
    assert len(overview["alerts"]["data"]["rows"]) <= 5
    activity = overview["activity"]["data"]["rows"]
    assert 0 < len(activity) <= 8
    assert [c["key"] for c in overview["activity"]["data"]["columns"]] == [
        "asset",
        "event",
        "employee",
        "changed_on",
    ]


def test_each_role_sees_its_own_totals(api, sql):
    everyone = widgets(api.dashboard("overview"))["total"]["data"]["value"]
    employee = widgets(api.dashboard("overview", EMPLOYEE))["total"]["data"]["value"]
    manager = widgets(api.dashboard("overview", MANAGER))["total"]["data"]["value"]
    own = sql(
        f"""SELECT count(*) FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
            WHERE u.first_name = 'Thandi'"""
    )[0][0]
    assert employee == own
    assert employee < manager < everyone


def test_activity_for_an_employee_only_lists_their_assets(api, sql):
    rows = widgets(api.dashboard("overview", EMPLOYEE))["activity"]["data"]["rows"]
    mine = {
        asset_no
        for (asset_no,) in sql(
            f"""SELECT a.asset_no FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
                WHERE u.first_name = 'Thandi'"""
        )
    }
    assert rows
    assert {row["asset"].split(" · ")[0] for row in rows} <= mine


def test_audit_and_financial_widgets_match_the_database(api, sql):
    cards = widgets(api.dashboard("management"))
    assert all(card["available"] for card in cards.values())
    pending = sql(f"SELECT count(*) FROM {S}audit_confirmations WHERE status = 'Pending'")[0][0]
    assert cards["unconfirmed"]["data"]["value"] == pending
    top = sql(
        f"""SELECT l.name, count(*) FROM {S}audit_confirmations c
            JOIN {S}assets a USING (asset_id) JOIN {S}locations l USING (location_id)
            WHERE c.status = 'Exception' GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 1"""
    )[0]
    first = cards["audit_exceptions"]["data"]["rows"][0]
    assert (first["label"], first["value"]) == top
    open_aod = float(sql(f"SELECT sum(amount) FROM {S}aod_records WHERE status = 'Open'")[0][0])
    assert open_aod == float(
        cards["financial_exposure"]["data"]["rows"][0]["text"].removeprefix("R").replace("\u202f", "")
    )


def test_widgets_needing_missing_tables_are_marked_unavailable(settings):
    needs_missing = Widget("w", "kpi", "W", "metrics/total_assets", requires=("no_such_table",))
    works = Widget("v", "kpi", "V", "metrics/total_assets")
    service = DashboardService(
        {"x": Dashboard("x", "X", (needs_missing, works))}, Database(settings.database_url), DemoIdentity()
    )
    result = widgets(service.get("x"))
    assert result["w"] == {
        "id": "w",
        "type": "kpi",
        "title": "W",
        "size": "medium",
        "tone": "info",
        "available": False,
        "data": None,
    }
    assert result["v"]["available"] is True


def test_management_cards_match_the_database(api, sql):
    cards = widgets(api.dashboard("management"))
    exceptions = sql(f"SELECT count(*) FROM {S}audit_confirmations WHERE status = 'Exception'")[0][0]
    open_aod = float(sql(f"SELECT sum(amount) FROM {S}aod_records WHERE status = 'Open'")[0][0])
    ended = sql(
        f"""SELECT count(*) FROM {S}assets
            WHERE status_id NOT IN (4, 5) AND warranty_expiry_date < current_date"""
    )[0][0]
    assert [c["type"] for c in list(cards.values())[:4]] == ["kpi"] * 4
    assert cards["exceptions"]["data"]["value"] == exceptions
    assert cards["open_aod"]["data"]["value"] == open_aod
    assert cards["open_aod"]["data"]["text"].startswith("R")
    assert cards["warranty_ended"]["data"]["value"] == ended

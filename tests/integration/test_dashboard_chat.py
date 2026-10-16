"""Asking for dashboards and charts in the chat."""

import pytest

S = "asset_management."
EMPLOYEE = "thandi.nkosi@example.co.za"


def widget(api, dashboard: str, widget_id: str, email: str | None = None) -> dict:
    found = {w["id"]: w for w in api.dashboard(dashboard, email)["widgets"]}
    return found[widget_id]


def test_lists_dashboards_as_clickable_choices(api):
    reply = api.ask("What dashboards are there?")
    _, listed = api.get("/api/dashboards")
    assert (reply["scope"], reply["intent"]) == ("in", "list_dashboards")
    assert [chip["label"] for chip in reply["chips"]] == [d["title"] for d in listed]
    assert reply["answer"].startswith(f"**{len(listed)} dashboards**")


@pytest.mark.parametrize("name", ["Overview", "Operational", "Management"])
def test_clicking_a_choice_opens_that_dashboard(api, name):
    chip = next(c for c in api.ask("Show me the dashboards")["chips"] if c["label"] == name)
    reply = api.ask(chip["question"])
    assert reply["intent"] == "open_dashboard"
    assert reply["dashboard"]["id"] == name.lower()
    assert reply["dashboard"]["widgets"]


def test_a_dashboard_without_a_name_lists_the_choices(api):
    assert api.ask("open the dashboard")["intent"] == "list_dashboards"


def test_an_opened_dashboard_only_holds_what_the_user_may_see(api):
    everyone = api.ask("Open the Overview dashboard")["dashboard"]["widgets"][0]["data"]["value"]
    own = api.ask("Open the Overview dashboard", email=EMPLOYEE)["dashboard"]["widgets"][0]["data"]["value"]
    assert own < everyone


@pytest.mark.parametrize(
    ("question", "topic", "months"),
    [
        ("Show purchases as a chart", "operational.purchases", 12),
        ("Show the repair cost trend", "operational.repair_cost", 6),
        ("Warranties ending over time", "operational.warranty_expiries", 6),
    ],
)
def test_trend_charts_use_the_dashboard_numbers(api, question, topic, months):
    reply = api.ask(question)
    expected = widget(api, *topic.split("."))["data"]["rows"]
    assert reply["slots"] == {"chart": topic}
    assert reply["chart"]["kind"] == "columns"
    assert len(reply["chart"]["rows"]) == months
    assert [r["value"] for r in reply["chart"]["rows"]] == [r["value"] for r in expected]


def test_a_chart_for_a_role_only_counts_what_the_role_sees(api):
    reply = api.ask("Show purchases as a chart", email=EMPLOYEE)
    expected = widget(api, "operational", "purchases", EMPLOYEE)["data"]["rows"]
    everyone = widget(api, "operational", "purchases")["data"]["rows"]
    assert [r["value"] for r in reply["chart"]["rows"]] == [r["value"] for r in expected]
    assert sum(r["value"] for r in reply["chart"]["rows"]) < sum(r["value"] for r in everyone)


def test_this_as_a_chart_after_a_cost_comparison_shows_the_trend(api):
    first = api.ask("Compare purchase spend this month and last month")
    reply = api.ask("show this as a chart", {"intent": first["intent"], "slots": first["slots"]})
    assert reply["slots"] == {"chart": "operational.purchases"}
    assert reply["chart"]["kind"] == "columns"


def test_this_as_a_chart_after_a_count_splits_the_same_assets(api, sql):
    first = api.ask("How many laptops are available?")
    reply = api.ask("give me this in a chart format", {"intent": first["intent"], "slots": first["slots"]})
    expected = sql(f"SELECT count(*) FROM {S}assets WHERE asset_type_id = 1 AND status_id = 1")[0][0]
    assert reply["intent"] == "breakdown_assets"
    assert reply["slots"]["group_by"] == "location"
    assert sum(row["value"] for row in reply["chart"]["rows"]) == expected


def test_a_chart_request_that_names_filters_splits_the_register(api, sql):
    reply = api.ask("chart my monitors")
    expected = sql(f"SELECT count(*) FROM {S}assets WHERE asset_type_id = 3")[0][0]
    assert reply["intent"] == "breakdown_assets"
    assert sum(row["value"] for row in reply["chart"]["rows"]) == expected


def test_a_trend_chart_says_when_it_cannot_apply_a_filter(api):
    assert "not applied" in api.ask("Show the purchases chart for laptops")["source"]


def test_a_chart_with_nothing_to_chart_asks_what_to_chart(api):
    reply = api.ask("chart it")
    assert reply["scope"] == "out"
    assert "Tell me what to chart" in reply["answer"]

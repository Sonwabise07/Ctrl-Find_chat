import pytest

from assistant.catalog import load_catalog
from assistant.dashboards.catalog import load_chart_topics
from assistant.data.lookups import Lookups, Person
from assistant.understanding.charts import ChartResolver
from assistant.understanding.entities import find_unknown_entity
from assistant.understanding.rules import RuleClassifier
from assistant.understanding.slots import SlotExtractor
from assistant.vocabulary import load_vocabulary

LOOKUPS = Lookups(
    locations=["Sandton HQ", "Umhlanga", "Midrand DC"],
    departments=["IT", "Finance", "Sales"],
    asset_types=["Laptop", "Monitor"],
    statuses=["Available", "Assigned", "In Maintenance", "Retired", "Lost"],
    makes=["Dell", "MacBook"],
    people=[Person(1, "Thandi", "Nkosi"), Person(2, "Thabo", "Baloyi")],
)
VOCAB = load_vocabulary()
EXTRACTOR = SlotExtractor(VOCAB)
RULES = RuleClassifier(load_catalog(), VOCAB, EXTRACTOR)


def test_slots_come_from_values_in_the_database():
    slots = EXTRACTOR.extract("Show available laptops at Sandton", LOOKUPS)
    assert slots["asset_type"] == "Laptop"
    assert slots["status"] == "Available"
    assert slots["location"] == "Sandton HQ"


def test_unique_first_name_resolves_a_person_but_a_clash_does_not():
    assert EXTRACTOR.extract("what does Thandi have", LOOKUPS)["person"] == 1
    assert "person" not in EXTRACTOR.extract("what does Tha have", LOOKUPS)


def test_next_n_days_window_is_capped():
    assert EXTRACTOR.extract("warranty ending in the next 900 days", LOOKUPS)["window"] == "days:365"


@pytest.mark.parametrize(
    ("question", "intent"),
    [
        ("How many laptops are available?", "count_assets"),
        ("Show me the monitors", "list_assets"),
        ("Which confirmations are overdue?", "overdue_confirmations"),
        ("What is the open AOD value?", "open_aod_value"),
        ("Compare repair costs this month and last month", "maintenance_cost_by_period"),
        ("What's our total headcount?", "out_of_scope"),
        ("asdf qwerty", "out_of_scope"),
    ],
)
def test_rule_classifier_picks_the_question_type(question, intent):
    assert RULES.classify(question, LOOKUPS, None)[0] == intent


def test_only_unknown_places_are_flagged():
    assert find_unknown_entity("How many monitors are in Cape Town?", LOOKUPS, VOCAB) == "Cape Town"
    assert find_unknown_entity("How many monitors are in Sandton?", LOOKUPS, VOCAB) is None


DASHBOARD_EXTRACTOR = SlotExtractor(VOCAB, {"overview": "Overview", "operational": "Operational"})
DASHBOARD_RULES = RuleClassifier(load_catalog(), VOCAB, DASHBOARD_EXTRACTOR)
CHARTS = ChartResolver(load_chart_topics())


@pytest.mark.parametrize(
    ("question", "intent", "slots"),
    [
        ("What dashboards are there?", "list_dashboards", {}),
        ("Open the Operational dashboard", "open_dashboard", {"dashboard": "operational"}),
        ("open the dashboard", "list_dashboards", {}),
        ("Show purchases as a chart", "show_chart", {}),
        ("list all the asset type we have", "breakdown_assets", {"group_by": "type"}),
        ("What types of assets do we have?", "breakdown_assets", {"group_by": "type"}),
    ],
)
def test_dashboard_and_chart_requests_are_recognised(question, intent, slots):
    found_intent, found_slots = DASHBOARD_RULES.classify(question, LOOKUPS, None)
    assert found_intent == intent
    assert {k: found_slots[k] for k in slots} == slots


def test_a_chart_follows_up_the_question_type_it_belongs_to():
    topic = CHARTS.resolve("show this as a chart", {}, {"intent": "warranty_assets"}).topic
    assert topic.id == "operational.warranty_expiries"


def test_naming_a_topic_beats_the_previous_question():
    resolution = CHARTS.resolve("chart the repair trend", {}, {"intent": "spend_by_period"})
    assert resolution.topic.id == "operational.repair_cost"


@pytest.mark.parametrize(
    ("filters", "split"),
    [
        ({"asset_type": "Laptop", "status": "Available"}, "location"),
        ({"asset_type": "Laptop"}, "status"),
        ({"status": "Available"}, "type"),
        ({}, "status"),
    ],
)
def test_a_split_never_uses_a_dimension_the_filters_already_fix(filters, split):
    resolution = CHARTS.resolve("chart this", filters, {"intent": "count_assets", "slots": filters})
    assert resolution.intent == "breakdown_assets"
    assert resolution.slots["group_by"] == split


def test_nothing_to_chart_gives_no_resolution():
    assert CHARTS.resolve("chart it", {}, None) is None

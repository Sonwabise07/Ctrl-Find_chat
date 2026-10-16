import pytest

from assistant.catalog import load_catalog
from assistant.data.lookups import available_intents
from assistant.understanding.rules import RuleClassifier
from assistant.understanding.slots import SlotExtractor
from assistant.vocabulary import load_vocabulary
from tests.unit.test_understanding import LOOKUPS

CATALOG = load_catalog()
VOCAB = load_vocabulary()
RULES = RuleClassifier(CATALOG, VOCAB, SlotExtractor(VOCAB))


@pytest.mark.parametrize(
    ("question", "intent"),
    [
        ("What am I responsible for?", "my_assets"),
        ("What do I have?", "my_assets"),
        ("Show my laptops", "my_assets"),
        ("Show my team's assets", "team_assets"),
        ("What does my department have?", "team_assets"),
        ("Show the history of AST-0013", "asset_timeline"),
        ("what happened to ast0013?", "asset_timeline"),
        ("Tell me about AST-0013", "asset_lookup"),
        ("Which assets are still held by people who have left?", "unrecovered_assets"),
        ("Show assets not yet recovered from leavers", "unrecovered_assets"),
        ("Show open loss and theft cases", "open_loss_cases"),
        ("How many assets were stolen?", "open_loss_cases"),
        ("Who has an open AOD?", "aod_cases"),
        ("Show open AOD cases", "aod_cases"),
        ("How old are our laptops?", "laptop_ages"),
    ],
)
def test_new_questions_reach_their_question_type(question, intent):
    assert RULES.classify(question, LOOKUPS, None)[0] == intent


@pytest.mark.parametrize(
    ("question", "intent"),
    [
        ("What is the open AOD value?", "open_aod_value"),
        ("How many lost phones are there?", "count_assets"),
        ("What does Thandi Nkosi have?", "assets_of_person"),
        ("How many laptops are older than 1 year?", "count_assets"),
        ("Show assets that are no longer under warranty", "warranty_assets"),
        ("Which office has the most audit exceptions?", "audit_exceptions_by_location"),
        ("How many laptops do we have in total?", "count_assets"),
    ],
)
def test_older_questions_keep_their_question_type(question, intent):
    assert RULES.classify(question, LOOKUPS, None)[0] == intent


def test_its_history_follows_an_asset_card_and_only_then():
    after_card = {"intent": "asset_lookup", "slots": {"asset_ref": "AST0013"}}
    intent, slots = RULES.classify("show its history", LOOKUPS, after_card)
    assert (intent, slots["asset_ref"]) == ("asset_timeline", "AST0013")
    assert RULES.classify("show its history", LOOKUPS, None)[0] != "asset_timeline"


def test_questions_that_need_missing_tables_are_not_available():
    without_migration = available_intents(set(), CATALOG)
    assert {"open_loss_cases", "aod_cases", "unconfirmed_assets"}.isdisjoint(without_migration)
    assert {"my_assets", "asset_timeline", "unrecovered_assets", "laptop_ages"} <= without_migration
    assert {"open_loss_cases", "aod_cases"} <= available_intents({"loss_cases", "aod_records"}, CATALOG)

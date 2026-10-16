from ..catalog import Catalog
from ..data.lookups import Lookups
from ..queries.runner import QueryResult
from ..vocabulary import Vocabulary
from . import assets, cases, comparisons, counts, lists, ownership, ranges, rankings, timeline
from .models import Answer, Facts

FORMATTERS = {
    "count_assets": counts.count_assets,
    "breakdown_assets": counts.breakdown_assets,
    "audit_exceptions_by_location": counts.audit_exceptions_by_location,
    "spend_by_period": comparisons.period_comparison("spend_by_period"),
    "maintenance_cost_by_period": comparisons.period_comparison("maintenance_cost_by_period"),
    "open_aod_value": comparisons.open_aod_value,
    "list_assets": lists.list_assets,
    "warranty_assets": lists.warranty_assets,
    "maintenance_open": lists.maintenance_open,
    "assets_of_person": lists.assets_of_person,
    "unconfirmed_assets": lists.unconfirmed_assets,
    "overdue_confirmations": lists.overdue_confirmations,
    "asset_lookup": assets.asset_lookup,
    "ranking": rankings.ranking,
    "purchases_in_period": ranges.purchases_in_period,
    "repairs_in_period": ranges.repairs_in_period,
    "my_assets": ownership.my_assets,
    "team_assets": ownership.team_assets,
    "asset_timeline": timeline.asset_timeline,
    "unrecovered_assets": cases.unrecovered_assets,
    "open_loss_cases": cases.open_loss_cases,
    "aod_cases": cases.aod_cases,
    "laptop_ages": lists.laptop_ages,
}


def build_answer(
    intent: str, slots: dict, result: QueryResult, catalog: Catalog, vocab: Vocabulary, lookups: Lookups
) -> Answer:
    definition = catalog.intents[intent]
    facts = Facts(
        slots=slots,
        rows=result.rows,
        window=result.window,
        columns=definition.columns,
        source=f"Based on {definition.source} as of today.",
        vocab=vocab,
        lookups=lookups,
    )
    return FORMATTERS[intent](facts)

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ..catalog import Catalog
from ..filters import FILTER_SLOTS
from ..identity import CurrentUser
from .periods import Window, comparison_periods, warranty_window

SQL_DIR = Path(__file__).parent.parent / "sql"
PERIOD_INTENTS = {"spend_by_period", "maintenance_cost_by_period"}
DEFAULT_RANK_LIMIT = 5

# Every query reads from `scoped`, so a user can never see assets outside their role's access.
SCOPE_CTE = """WITH scoped AS (
    SELECT a.* FROM asset_management.assets a
    WHERE %(scope_all)s
       OR a.assigned_to_user_id = %(scope_user)s
       OR a.department_id = %(scope_department)s
) """


def access_params(user: CurrentUser) -> dict:
    """Query values that the `scoped` list of assets is built from."""
    return {
        "scope_all": user.sees_everything,
        "scope_user": user.id,
        "scope_department": user.scope_department_id,
        "user_department": user.department_id,
    }


@dataclass(frozen=True)
class QueryResult:
    rows: list[dict]
    window: Window | None = None


class QueryRunner:
    def __init__(self, catalog: Catalog, sql_dir: Path = SQL_DIR):
        joins = (sql_dir / "_joins.sql").read_text()
        filters = (sql_dir / "_filters.sql").read_text()
        self._date_range_intents = {n for n, i in catalog.intents.items() if i.needs_date_range}
        self._optional = {
            name: tuple(
                (frozenset(part.requires), (sql_dir / f"{part.sql}.sql").read_text()) for part in i.optional
            )
            for name, i in catalog.intents.items()
            if i.optional
        }
        files = {name: sql_dir / f"{name}.sql" for name in catalog.intents}
        self._sql = {  # dashboards and charts have no query of their own
            name: SCOPE_CTE + file.read_text().replace("{{JOINS}}", joins).replace("{{FILTERS}}", filters)
            for name, file in files.items()
            if file.exists()
        }

    def run(
        self,
        cursor,
        intent: str,
        slots: dict,
        user: CurrentUser,
        today: date | None = None,
        tables: frozenset[str] | set[str] = frozenset(),
    ) -> QueryResult:
        """`tables` are the tables that exist now. Optional parts of a query that need others are left out."""
        today = today or date.today()
        params = dict.fromkeys((*FILTER_SLOTS, "date_from", "date_to"))
        params.update({key: slots[key] for key in FILTER_SLOTS if key in slots})
        params.update(
            group_by=slots.get("group_by", "status"),
            person_id=slots.get("person"),
            asset_ref=slots.get("asset_ref"),
            rank_metric=slots.get("rank_metric", "count"),
            rank_order=slots.get("rank_order", "desc"),
            rank_limit=slots.get("rank_limit", DEFAULT_RANK_LIMIT),
            **access_params(user),
        )
        window = None
        if intent == "warranty_assets":
            window = warranty_window(slots.get("window", "days:30"), today)
            params.update(date_from=window.start, date_to=window.end)
        if intent in self._date_range_intents:
            params.update(
                date_from=date.fromisoformat(slots["date_from"]), date_to=date.fromisoformat(slots["date_to"])
            )
        if intent in PERIOD_INTENTS:
            earlier, later = comparison_periods(slots.get("period", "month"), today)
            for prefix, period in (("p1", earlier), ("p2", later)):
                params.update(
                    {
                        f"{prefix}_label": period.label,
                        f"{prefix}_start": period.start,
                        f"{prefix}_end": period.end,
                    }
                )
        cursor.execute(self._with_optional_parts(intent, tables), params)
        return QueryResult(cursor.fetchall(), window)

    def _with_optional_parts(self, intent: str, tables) -> str:
        parts = (text for needs, text in self._optional.get(intent, ()) if needs <= tables)
        return self._sql[intent].replace("{{EXTRA_EVENTS}}", "\n".join(parts))

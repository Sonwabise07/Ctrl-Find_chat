import json
from dataclasses import dataclass
from pathlib import Path

CONFIG_DIR = Path(__file__).parent / "config"
OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True)
class OptionalSql:
    """A piece of query that is only included when the tables it needs exist."""

    sql: str
    requires: tuple[str, ...]


@dataclass(frozen=True)
class Intent:
    name: str
    slots: tuple[str, ...]
    source: str
    example: str
    requires: tuple[str, ...] = ()
    columns: tuple[str, ...] = ()
    uses_dates: bool = False  # a date range in the question is something this intent can apply
    needs_date_range: bool = False
    optional: tuple[OptionalSql, ...] = ()


@dataclass(frozen=True)
class Category:
    label: str
    intents: tuple[str, ...]


@dataclass(frozen=True)
class Chip:
    label: str
    question: str


@dataclass(frozen=True)
class Catalog:
    intents: dict[str, Intent]
    categories: tuple[Category, ...]
    chips: tuple[Chip, ...]

    @property
    def required_tables(self) -> set[str]:
        return {table for intent in self.intents.values() for table in intent.requires}

    @property
    def all_tables(self) -> set[str]:
        """Every table any question type may use, including its optional parts."""
        optional = {t for i in self.intents.values() for part in i.optional for t in part.requires}
        return self.required_tables | optional


def load_catalog(path: Path = CONFIG_DIR / "intents.json") -> Catalog:
    raw = json.loads(path.read_text(encoding="utf-8"))
    intents = {
        name: Intent(
            name=name,
            slots=tuple(item["slots"]),
            source=item["source"],
            example=item["example"],
            requires=tuple(item["requires"]),
            columns=tuple(item.get("columns", ())),
            uses_dates=item.get("uses_dates", False),
            needs_date_range=item.get("needs_date_range", False),
            optional=tuple(OptionalSql(p["sql"], tuple(p["requires"])) for p in item.get("optional", ())),
        )
        for name, item in raw["intents"].items()
    }
    return Catalog(
        intents=intents,
        categories=tuple(Category(c["label"], tuple(c["intents"])) for c in raw["categories"]),
        chips=tuple(Chip(**chip) for chip in raw["chips"]),
    )

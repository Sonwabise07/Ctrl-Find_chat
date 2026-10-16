from dataclasses import dataclass, field

from ..data.lookups import Lookups
from ..queries.periods import Window
from ..vocabulary import Vocabulary


@dataclass
class Chart:
    rows: list[dict]  # each row: label, value, text
    note: str
    kind: str = "bars"  # "bars" for comparing groups, "columns" for change over time


@dataclass
class Table:
    columns: list[str]
    rows: list[dict]


@dataclass
class Details:
    """Label and value pairs about one thing, such as an asset."""

    title: str
    rows: list[dict]  # each row: label, text


@dataclass
class Answer:
    text: str
    source: str
    chart: Chart | None = None
    table: Table | None = None
    details: Details | None = None


@dataclass(frozen=True)
class Facts:
    """Everything a formatter needs. Formatters only read from here, so every figure traces to a row."""

    slots: dict
    rows: list[dict]
    window: Window | None
    columns: tuple[str, ...]
    source: str
    vocab: Vocabulary
    lookups: Lookups
    total: int = field(init=False)

    def __post_init__(self):
        has_total = self.rows and "total" in self.rows[0]
        object.__setattr__(self, "total", int(self.rows[0]["total"]) if has_total else len(self.rows))

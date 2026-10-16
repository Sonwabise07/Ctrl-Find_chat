from dataclasses import dataclass

from ..catalog import Catalog

SCHEMA = "asset_management"
_VALUE_QUERIES = {
    "locations": "SELECT name FROM asset_management.locations",
    "departments": "SELECT name FROM asset_management.departments",
    "asset_types": "SELECT name FROM asset_management.asset_types",
    "statuses": "SELECT name FROM asset_management.asset_statuses",
    "makes": """SELECT DISTINCT split_part(description, ' ', 1) AS name
                FROM asset_management.assets WHERE description IS NOT NULL""",
}


@dataclass(frozen=True)
class Person:
    id: int
    first_name: str
    last_name: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass(frozen=True)
class Lookups:
    """Values that currently exist in the database. Questions are only matched against these."""

    locations: list[str]
    departments: list[str]
    asset_types: list[str]
    statuses: list[str]
    makes: list[str]
    people: list[Person]

    def person_name(self, person_id: int | None) -> str | None:
        return next((p.full_name for p in self.people if p.id == person_id), None)


def load_lookups(cursor) -> Lookups:
    values = {}
    for key, query in _VALUE_QUERIES.items():
        cursor.execute(query)
        values[key] = [row["name"] for row in cursor.fetchall()]
    cursor.execute(
        """SELECT user_id AS id, first_name, last_name
           FROM asset_management.users WHERE is_active"""
    )
    return Lookups(**values, people=[Person(**row) for row in cursor.fetchall()])


def existing_tables(cursor, tables: set[str]) -> set[str]:
    cursor.execute(
        """SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
           WHERE n.nspname = %s AND c.relname = ANY(%s)""",
        (SCHEMA, list(tables)),
    )
    return {row["relname"] for row in cursor.fetchall()}


def table_inventory(cursor, catalog: Catalog) -> set[str]:
    """The tables, among all the ones question types use, that exist right now."""
    return existing_tables(cursor, catalog.all_tables)


def available_intents(existing: set[str], catalog: Catalog) -> set[str]:
    """Intents whose required tables exist, so a missing migration degrades to a plain refusal."""
    return {n for n, intent in catalog.intents.items() if set(intent.requires) <= existing}

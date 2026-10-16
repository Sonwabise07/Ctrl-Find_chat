import json
import re
from dataclasses import dataclass
from pathlib import Path

from .catalog import CONFIG_DIR


def _compile(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.IGNORECASE)


@dataclass(frozen=True)
class Route:
    intent: str
    patterns: tuple[re.Pattern, ...]

    def matches(self, text: str) -> bool:
        return all(pattern.search(text) for pattern in self.patterns)


@dataclass(frozen=True)
class Ranking:
    highest: re.Pattern
    lowest: re.Pattern
    value: re.Pattern
    limit: re.Pattern
    dimensions: tuple[tuple[re.Pattern, str], ...]
    blockers: re.Pattern


@dataclass(frozen=True)
class Vocabulary:
    blocked: re.Pattern
    people: re.Pattern
    asset_nouns: re.Pattern
    phrases: dict[str, re.Pattern]
    routes: tuple[Route, ...]
    type_patterns: dict[str, re.Pattern]
    type_nouns: dict[str, str]
    type_terms: frozenset[str]
    status_patterns: dict[str, re.Pattern]
    status_phrases: dict[str, str]
    makes: frozenset[str]
    months: frozenset[str]
    warranty_windows: tuple[tuple[re.Pattern, str], ...]
    group_by: tuple[tuple[re.Pattern, str], ...]
    ranking: Ranking
    messages: dict[str, str]

    def is_blocked(self, text: str) -> bool:
        return bool(self.blocked.search(text))


def load_vocabulary(path: Path = CONFIG_DIR / "vocabulary.json") -> Vocabulary:
    raw = json.loads(path.read_text(encoding="utf-8"))
    types, statuses = raw["types"], raw["statuses"]
    return Vocabulary(
        blocked=_compile(raw["blocked"]),
        people=_compile(raw["people"]),
        asset_nouns=_compile(raw["asset_nouns"]),
        phrases={name: _compile(pattern) for name, pattern in raw["phrases"].items()},
        routes=tuple(Route(r["intent"], tuple(_compile(p) for p in r["all"])) for r in raw["routes"]),
        type_patterns={n: _compile(rf"\b({t['pattern']})\b") for n, t in types.items()},
        type_nouns={n: t["noun"] for n, t in types.items()},
        type_terms=frozenset(re.findall(r"[a-z]+", " ".join(t["pattern"] for t in types.values()))),
        status_patterns={n: _compile(s["pattern"]) for n, s in statuses.items()},
        status_phrases={n: s["phrase"] for n, s in statuses.items()},
        makes=frozenset(raw["makes"]),
        months=frozenset(raw["months"]),
        warranty_windows=tuple((_compile(p), value) for p, value in raw["warranty_windows"]),
        group_by=tuple((_compile(p), value) for p, value in raw["group_by"]),
        ranking=_ranking(raw["ranking"]),
        messages=raw["messages"],
    )


def _ranking(raw: dict) -> Ranking:
    return Ranking(
        highest=_compile(rf"\b({raw['highest']})\b"),
        lowest=_compile(rf"\b({raw['lowest']})\b"),
        value=_compile(rf"\b({raw['value']})\b"),
        limit=_compile(raw["limit"]),
        dimensions=tuple((_compile(rf"\b({p})\b"), value) for p, value in raw["dimensions"]),
        blockers=_compile(raw["blockers"]),
    )

from ..vocabulary import Vocabulary
from .dates import NUMBER_WORDS

DEFAULT_LIMIT = 5
MAX_LIMIT = 20


def parse_ranking(text: str, vocab: Vocabulary) -> dict | None:
    """Reads 'which location has the most laptops' or 'top 3 departments by value' into ranking slots."""
    words = vocab.ranking
    if words.blockers.search(text):
        return None
    highest, lowest = words.highest.search(text), words.lowest.search(text)
    group = next((value for pattern, value in words.dimensions if pattern.search(text)), None)
    if not (highest or lowest) or group is None:
        return None
    return {
        "group_by": group,
        "rank_order": "asc" if lowest and not highest else "desc",
        "rank_metric": "value" if words.value.search(text) else "count",
        "rank_limit": _limit(text, words),
    }


def _limit(text, words) -> int:
    match = words.limit.search(text)
    if not match:
        return DEFAULT_LIMIT
    raw = match.group(1)
    number = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
    return max(1, min(number, MAX_LIMIT))

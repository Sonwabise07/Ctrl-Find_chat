import re

from ..data.lookups import Lookups
from ..vocabulary import Vocabulary
from .references import ASSET_NUMBER

PLACE_AFTER_PREPOSITION = re.compile(r"\b(?:in|at|for|from|of)\s+(?:the\s+)?([A-Z][\w&]*(?:\s+[A-Z][\w&]*)*)")
PRONOUNS = {"i", "it", "how", "what", "which"}


def find_unknown_entity(text: str, lookups: Lookups, vocab: Vocabulary) -> str | None:
    """Returns a capitalised name such as 'Cape Town' that the database does not hold."""
    text = ASSET_NUMBER.sub(" ", text)  # an asset number such as AST-9999 is not a place name
    known = _known_words(lookups, vocab)
    places = [name.lower() for name in lookups.locations + lookups.departments]
    for match in PLACE_AFTER_PREPOSITION.finditer(text):
        phrase = match.group(1).strip()
        words = phrase.lower().split()
        if phrase.lower() in known or phrase.lower() in PRONOUNS:
            continue
        if any(word in known for word in words):
            continue
        if any(place.startswith(words[0]) for place in places):
            continue
        return phrase
    return None


def _known_words(lookups: Lookups, vocab: Vocabulary) -> set[str]:
    names = lookups.locations + lookups.departments + lookups.makes
    known = {name.lower() for name in names} | vocab.type_terms | vocab.months
    for person in lookups.people:
        known |= {person.first_name.lower(), person.last_name.lower()}
    return known

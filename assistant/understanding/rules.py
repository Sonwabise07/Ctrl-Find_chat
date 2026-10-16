from ..catalog import OUT_OF_SCOPE, Catalog
from ..data.lookups import Lookups
from ..filters import FILTER_SLOTS
from ..vocabulary import Vocabulary
from .slots import SlotExtractor

ASSET_INTENTS = {"asset_lookup", "asset_timeline"}
NON_DATA_INTENTS = {"list_dashboards", "open_dashboard", "show_chart", *ASSET_INTENTS}
FOLLOW_UP_MAX_WORDS = 6
AVAILABLE = "Available"


class RuleClassifier:
    """Keyword based fallback that works without a language model."""

    def __init__(self, catalog: Catalog, vocab: Vocabulary, extractor: SlotExtractor):
        self.catalog = catalog
        self.vocab = vocab
        self.extractor = extractor

    def classify(self, text: str, lookups: Lookups, context: dict | None) -> tuple[str, dict]:
        lowered = text.lower()
        slots = self.extractor.extract(text, lookups)
        if self.vocab.is_blocked(lowered):
            return OUT_OF_SCOPE, slots
        intent = (
            self._by_dashboard(lowered, slots)
            or self._by_asset(lowered, slots, context)
            or self._by_ranking(slots)
            or self._by_period(lowered, slots)
            or self._by_route(lowered)
            or self._by_slots(lowered, slots)
        )
        if intent is None:
            intent, slots = self._follow_up(lowered, slots, context)
        if intent in ("count_assets", "list_assets"):
            self._default_to_available(lowered, slots)
        return intent or OUT_OF_SCOPE, slots

    def _by_dashboard(self, text, slots):
        if not self.vocab.phrases["dashboard"].search(text):
            return None
        return "open_dashboard" if "dashboard" in slots else "list_dashboards"

    def _by_asset(self, text, slots, context):
        """An asset number means a lookup, or its history when the question asks for that."""
        phrases = self.vocab.phrases
        asks_history = phrases["timeline"].search(text)
        if "asset_ref" in slots:
            return "asset_timeline" if asks_history else "asset_lookup"
        earlier = (context or {}).get("slots") or {}
        about_it = phrases["this_asset"].search(text) and (context or {}).get("intent") in ASSET_INTENTS
        if asks_history and about_it and "asset_ref" in earlier:
            slots["asset_ref"] = earlier["asset_ref"]  # "show its history" after an asset card
            return "asset_timeline"
        return None

    @staticmethod
    def _by_ranking(slots):
        return "ranking" if "rank_order" in slots else None

    def _by_period(self, text, slots):
        """Purchases or repairs in a period. Comparisons and charts keep their own routes."""
        phrases = self.vocab.phrases
        if "date_from" not in slots or phrases["chart"].search(text) or phrases["compare"].search(text):
            return None
        if phrases["repair_words"].search(text):
            return "repairs_in_period"
        return "purchases_in_period" if phrases["purchase_words"].search(text) else None

    def _by_route(self, text):
        return next((r.intent for r in self.vocab.routes if r.matches(text)), None)

    def _by_slots(self, text, slots):
        phrases = self.vocab.phrases
        wants_stock = phrases["spare"].search(text)
        if "person" in slots and phrases["holds"].search(text):
            return "assets_of_person"
        if wants_stock and "asset_type" not in slots and not phrases["how_many"].search(text):
            slots.setdefault("group_by", "type")
            slots["status"] = AVAILABLE
            return "breakdown_assets"
        names_asset = self.vocab.asset_nouns.search(text) or "asset_type" in slots or "make" in slots
        if not names_asset:
            return None
        if "group_by" in slots:
            return "breakdown_assets"
        if phrases["count"].search(text):
            return "count_assets"
        if phrases["list"].search(text):
            return "list_assets"
        if wants_stock:
            slots.setdefault("status", AVAILABLE)
            return "count_assets"
        return None

    def _follow_up(self, text, slots, context):
        """A short reply such as 'and monitors?' keeps the previous question type."""
        previous = (context or {}).get("intent")
        is_short = len(text.split()) <= FOLLOW_UP_MAX_WORDS
        if previous not in self.catalog.intents or previous in NON_DATA_INTENTS or not is_short:
            return None, slots
        if not any(key in slots for key in FILTER_SLOTS):
            return None, slots
        carried = {k: v for k, v in (context.get("slots") or {}).items() if k != "person"}
        current = {k: v for k, v in slots.items() if k != "period"}
        return previous, {**carried, **current}

    def _default_to_available(self, text, slots):
        if slots.get("status") is None and self.vocab.phrases["spare"].search(text):
            slots["status"] = AVAILABLE

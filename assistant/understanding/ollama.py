import json
import re
import urllib.request

from ..catalog import OUT_OF_SCOPE, Catalog
from ..data.lookups import Lookups
from ..settings import Settings
from .slots import SlotExtractor

REQUEST_TIMEOUT_SECONDS = 60
GROUP_BY_VALUES = ["status", "type", "location", "department"]
# Read from the question text by the slot extractor. A model's version of these is ignored.
EXTRACTOR_ONLY = {
    "person", "asset_ref", "date_from", "date_to", "date_label",
    "rank_metric", "rank_order", "rank_limit", "older_than",
}  # fmt: skip
PERIOD_VALUES = ["month", "quarter"]
WINDOW_FORMAT = re.compile(r"expired|this_month|next_month|days:\d{1,3}")


class OllamaClassifier:
    """Asks a local model to pick one supported question type. The model never answers or writes SQL."""

    def __init__(
        self,
        settings: Settings,
        catalog: Catalog,
        extractor: SlotExtractor,
        dashboard_ids: list[str],
        chart_ids: list[str],
    ):
        self.settings = settings
        self.catalog = catalog
        self.extractor = extractor
        self.dashboard_ids = dashboard_ids
        self.chart_ids = chart_ids

    def classify(self, text, lookups: Lookups, available: set[str], context) -> tuple[str, dict]:
        reply = self._chat(self._system_prompt(lookups, available, context), text)
        intent = reply.get("intent", OUT_OF_SCOPE)
        if intent not in self.catalog.intents:
            return OUT_OF_SCOPE, {}
        slots = self._validated_slots(intent, reply.get("slots") or {}, lookups)
        # Dictionary matches fill any gaps; slots the model supplied and we validated take priority.
        return intent, {**self.extractor.extract(text, lookups), **slots}

    def _validated_slots(self, intent: str, proposed: dict, lookups: Lookups) -> dict:
        allowed = set(self.catalog.intents[intent].slots) - EXTRACTOR_ONLY
        options = {
            "asset_type": lookups.asset_types,
            "status": lookups.statuses,
            "location": lookups.locations,
            "department": lookups.departments,
            "make": lookups.makes,
            "group_by": GROUP_BY_VALUES,
            "period": PERIOD_VALUES,
            "dashboard": self.dashboard_ids,
            "chart": self.chart_ids,
        }
        slots = {
            key: value
            for key, value in proposed.items()
            if key in allowed and (key not in options or value in options[key])
        }
        window = str(proposed.get("window", ""))
        if "window" in allowed and WINDOW_FORMAT.fullmatch(window):
            slots["window"] = window
        return slots

    def _system_prompt(self, lookups: Lookups, available: set[str], context) -> str:
        intents = {
            name: {"slots": intent.slots, "example": intent.example}
            for name, intent in self.catalog.intents.items()
            if name in available
        }
        prompt = (
            "You map a user question to ONE intent from the list, or 'out_of_scope'. "
            "Never answer the question. "
            'Reply with JSON only: {"intent": string, "slots": object}. '
            "Only use slot values from these lists. "
            f"Intents: {json.dumps(intents)}. asset_type: {lookups.asset_types}. "
            f"status: {lookups.statuses}. location: {lookups.locations}. "
            f"department: {lookups.departments}. group_by: status|type|location|department. "
            "period: month|quarter. window: expired|this_month|next_month|days:N. "
            f"dashboard: {self.dashboard_ids}. chart: {self.chart_ids}. "
            "Use show_chart when the user asks for a chart, graph or trend, "
            "including 'show this as a chart'. "
            "If the question is about anything else (people, headcount, salaries, weather, "
            "or data not listed) use out_of_scope. "
        )
        return prompt + (f"Previous turn: {json.dumps(context)}" if context else "")

    def _chat(self, system: str, question: str) -> dict:
        body = json.dumps(
            {
                "model": self.settings.ollama_model,
                "temperature": 0,
                "stream": False,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": question},
                ],
            }
        ).encode()
        request = urllib.request.Request(
            f"{self.settings.ollama_url}/v1/chat/completions",
            body,
            {"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            content = json.loads(response.read())["choices"][0]["message"]["content"]
        return json.loads(content)

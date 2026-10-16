import logging
from dataclasses import asdict, dataclass, field, replace

from .answers import build_answer
from .answers.dashboards import chart_answer, list_answer, open_answer
from .answers.models import Answer, Chart, Details, Table
from .answers.number_guard import unexplained_numbers
from .catalog import OUT_OF_SCOPE, Catalog, Chip
from .dashboards.service import DashboardService
from .data.database import Database
from .data.lookups import Lookups, available_intents, load_lookups, table_inventory
from .identity import CurrentUser, DemoIdentity
from .queries.runner import QueryRunner
from .understanding.charts import ChartResolver
from .understanding.classifier import IntentClassifier, Understanding
from .understanding.entities import find_unknown_entity
from .vocabulary import Vocabulary

log = logging.getLogger(__name__)
SUGGESTION_COUNT = 2
CONTEXT_IGNORED_SLOTS = {"period"}


@dataclass
class Reply:
    scope: str  # "in" when answered from data, "out" when refused
    answer: str
    intent: str | None = None
    classifier: str | None = None
    slots: dict | None = None
    source: str | None = None
    chart: Chart | None = None
    table: Table | None = None
    details: Details | None = None
    dashboard: dict | None = None
    chips: list[Chip] = field(default_factory=list)


@dataclass(frozen=True)
class Turn:
    """Everything known about one question while it is being answered."""

    cursor: object
    question: str
    understood: Understanding
    context: dict | None
    email: str | None
    user: CurrentUser
    lookups: Lookups
    chips: list[Chip]
    tables: frozenset[str]  # the tables that exist now


class AssistantService:
    def __init__(
        self,
        catalog: Catalog,
        vocab: Vocabulary,
        database: Database,
        identity: DemoIdentity,
        classifier: IntentClassifier,
        runner: QueryRunner,
        dashboards: DashboardService,
        charts: ChartResolver,
    ):
        self.catalog = catalog
        self.vocab = vocab
        self.database = database
        self.identity = identity
        self.classifier = classifier
        self.runner = runner
        self.dashboards = dashboards
        self.charts = charts

    def ask(self, question: str, context: dict | None = None, email: str | None = None) -> dict:
        with self.database.cursor() as cursor:
            lookups = load_lookups(cursor)
            tables = frozenset(table_inventory(cursor, self.catalog))
            available = available_intents(tables, self.catalog)
            user = self.identity.resolve(cursor, email)
            chips = self._suggestions(question, available)

            if unknown := self._unknown_entity(question, lookups):
                return self._refuse(self._unknown_entity_message(unknown, lookups), chips)

            understood = self.classifier.classify(question, lookups, available, context)
            intent, slots = understood.intent, understood.slots
            refusal = self._refusal_for(question, intent, slots, available, user)
            if refusal:
                return self._refuse(refusal, chips, intent=intent, classifier=understood.classifier)

            turn = Turn(cursor, question, understood, context, email, user, lookups, chips, tables)
            handlers = {
                "list_dashboards": self._list_dashboards,
                "open_dashboard": self._open_dashboard,
                "show_chart": self._chart,
            }
            return handlers.get(intent, self._answer)(turn)

    def _answer(self, turn: Turn) -> dict:
        intent, slots = turn.understood.intent, turn.understood.slots
        result = self.runner.run(turn.cursor, intent, slots, turn.user, tables=turn.tables)
        answer = build_answer(intent, slots, result, self.catalog, self.vocab, turn.lookups)
        window_text = result.window.text if result.window else ""
        known = (window_text, slots.get("date_label", ""))
        return self._reply(
            turn, intent, slots, answer, result.rows, *known, chips=self._next_steps(intent, result.rows)
        )

    @staticmethod
    def _next_steps(intent: str, rows: list[dict]) -> list[Chip] | None:
        """Buttons that follow on from an answer."""
        if intent == "asset_lookup" and rows:
            return [Chip("Full history", f"Show the history of {rows[0]['asset_no']}")]
        return None

    def _list_dashboards(self, turn: Turn) -> dict:
        dashboards = self.dashboards.list()
        chips = [Chip(d["title"], f"Open the {d['title']} dashboard") for d in dashboards]
        answer = list_answer(dashboards)
        return self._reply(turn, "list_dashboards", {}, answer, [{"value": len(dashboards)}], chips=chips)

    def _open_dashboard(self, turn: Turn) -> dict:
        dashboard_id = turn.understood.slots.get("dashboard")
        dashboard = self.dashboards.get(dashboard_id, turn.email) if dashboard_id else None
        if dashboard is None:
            return self._list_dashboards(turn)
        slots = {"dashboard": dashboard_id}
        return self._reply(turn, "open_dashboard", slots, open_answer(dashboard), [], dashboard=dashboard)

    def _chart(self, turn: Turn) -> dict:
        understood = turn.understood
        resolution = self.charts.resolve(turn.question, understood.slots, turn.context)
        if resolution is None:
            message = self.vocab.messages["chart_unknown"]
            return self._refuse(message, turn.chips, intent="show_chart", classifier=understood.classifier)
        if resolution.topic is None:  # a split of the asset register, which the normal pipeline draws
            split = replace(understood, intent=resolution.intent, slots=resolution.slots)
            return self._answer(replace(turn, understood=split))
        topic = resolution.topic
        widget = self.dashboards.widget(topic.dashboard_id, topic.widget_id, turn.email)
        if widget is None or not widget["available"]:
            message = self.vocab.messages["not_held"]
            return self._refuse(message, turn.chips, intent="show_chart", classifier=understood.classifier)
        answer = chart_answer(widget, topic, resolution.filtered)
        rows = widget["data"]["rows"]
        return self._reply(turn, "show_chart", {"chart": topic.id}, answer, rows, widget["title"])

    def _reply(
        self,
        turn: Turn,
        intent: str,
        slots: dict,
        answer: Answer,
        rows: list[dict],
        *known_text: str,
        dashboard: dict | None = None,
        chips: list[Chip] | None = None,
    ) -> dict:
        """Builds the in-scope reply after checking that every number in the answer comes from the rows."""
        if unexplained_numbers(answer.text, rows, turn.question, *known_text):
            log.error("Number check failed for %r: %s", turn.question, answer.text)
            answer.text = self.vocab.messages["number_check_failed"]
        return asdict(
            Reply(
                scope="in",
                answer=answer.text,
                intent=intent,
                classifier=turn.understood.classifier,
                slots={k: v for k, v in slots.items() if k not in CONTEXT_IGNORED_SLOTS},
                source=answer.source,
                chart=answer.chart,
                table=answer.table,
                details=answer.details,
                dashboard=dashboard,
                chips=chips or [],
            )
        )

    def meta(self, email: str | None = None) -> dict:
        with self.database.cursor() as cursor:
            available = available_intents(table_inventory(cursor, self.catalog), self.catalog)
            user = self.identity.resolve(cursor, email)
        categories = [
            {"label": c.label, "available": all(name in available for name in c.intents)}
            for c in self.catalog.categories
        ]
        return {
            "chips": [asdict(chip) for chip in self.catalog.chips],
            "categories": categories,
            "user": {"name": user.name, "role": user.role},
        }

    def _unknown_entity(self, question: str, lookups: Lookups) -> str | None:
        if self.vocab.is_blocked(question):
            return None
        return find_unknown_entity(question, lookups, self.vocab)

    def _unknown_entity_message(self, name: str, lookups: Lookups) -> str:
        return self.vocab.messages["unknown_entity"].format(name=name, locations=", ".join(lookups.locations))

    def _refusal_for(
        self, question: str, intent: str, slots: dict, available: set[str], user: CurrentUser
    ) -> str | None:
        messages = self.vocab.messages
        if intent == OUT_OF_SCOPE or intent not in self.catalog.intents:
            hint = messages["people_hint"] if self.vocab.people.search(question) else ""
            return messages["out_of_scope"] + hint
        if intent not in available:
            return messages["not_held"]
        if intent == "assets_of_person" and "person" not in slots:
            return messages["person_not_found"]
        if intent == "team_assets" and user.department_id is None:
            return messages["team_unknown"]
        if intent in ("asset_lookup", "asset_timeline") and "asset_ref" not in slots:
            return messages["asset_ref_missing"]
        wanted = self.catalog.intents[intent]
        if wanted.needs_date_range and "date_from" not in slots:
            return messages["date_range_missing"]
        if "date_from" in slots and not wanted.uses_dates:
            return messages["date_unsupported"]
        return None

    def _suggestions(self, question: str, available: set[str]) -> list[Chip]:
        chips = self.catalog.chips
        if "open_aod_value" in available:
            return [c for c in chips if c.question != question][:SUGGESTION_COUNT]
        return list(chips[SUGGESTION_COUNT : 2 * SUGGESTION_COUNT])

    @staticmethod
    def _refuse(
        message: str, chips: list[Chip], intent: str | None = None, classifier: str | None = None
    ) -> dict:
        intent = None if intent == OUT_OF_SCOPE else intent
        return asdict(Reply(scope="out", answer=message, intent=intent, classifier=classifier, chips=chips))

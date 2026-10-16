from .catalog import load_catalog
from .dashboards.catalog import load_chart_topics, load_dashboards
from .dashboards.service import DashboardService
from .data.database import Database
from .identity import DemoIdentity
from .queries.runner import QueryRunner
from .service import AssistantService
from .settings import Settings
from .understanding.charts import ChartResolver
from .understanding.classifier import IntentClassifier
from .understanding.ollama import OllamaClassifier
from .understanding.rules import RuleClassifier
from .understanding.slots import SlotExtractor
from .vocabulary import load_vocabulary


def build_service(settings: Settings) -> AssistantService:
    catalog = load_catalog()
    vocab = load_vocabulary()
    dashboards = build_dashboards(settings)
    titles = {d.id: d.title for d in dashboards.dashboards.values()}
    extractor = SlotExtractor(vocab, titles)
    charts = ChartResolver(load_chart_topics())
    ollama = OllamaClassifier(settings, catalog, extractor, list(titles), charts.ids)
    classifier = IntentClassifier(settings, vocab, RuleClassifier(catalog, vocab, extractor), ollama)
    return AssistantService(
        catalog,
        vocab,
        Database(settings.database_url),
        DemoIdentity(),
        classifier,
        QueryRunner(catalog),
        dashboards,
        charts,
    )


def build_dashboards(settings: Settings) -> DashboardService:
    return DashboardService(load_dashboards(), Database(settings.database_url), DemoIdentity())

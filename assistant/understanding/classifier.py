import logging
import urllib.error
from dataclasses import dataclass

from ..catalog import OUT_OF_SCOPE
from ..data.lookups import Lookups
from ..settings import Settings
from ..vocabulary import Vocabulary
from .ollama import OllamaClassifier
from .rules import RuleClassifier

log = logging.getLogger(__name__)
OLLAMA_ERRORS = (urllib.error.URLError, TimeoutError, ValueError, KeyError, OSError)


@dataclass(frozen=True)
class Understanding:
    intent: str
    slots: dict
    classifier: str


class IntentClassifier:
    """Uses Ollama when it is available and falls back to the rule classifier otherwise."""

    def __init__(
        self, settings: Settings, vocab: Vocabulary, rules: RuleClassifier, ollama: OllamaClassifier
    ):
        self.mode = settings.classifier
        self.vocab = vocab
        self.rules = rules
        self.ollama = ollama

    def classify(self, text: str, lookups: Lookups, available: set[str], context) -> Understanding:
        if self.vocab.is_blocked(text):
            return Understanding(OUT_OF_SCOPE, {}, "rules")
        if self.mode in ("auto", "ollama"):
            try:
                intent, slots = self.ollama.classify(text, lookups, available, context)
                return Understanding(intent, slots, "ollama")
            except OLLAMA_ERRORS as error:
                if self.mode == "ollama":
                    raise
                log.warning("Ollama unavailable, using rules: %s", error)
        intent, slots = self.rules.classify(text, lookups, context)
        return Understanding(intent, slots, "rules")

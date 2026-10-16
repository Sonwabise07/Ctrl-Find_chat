import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = "postgresql://asset_assistant_ro:change_me@localhost/asset_hub"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    classifier: str = "auto"  # auto, ollama or rules
    port: int = 8000

    @classmethod
    def from_env(cls) -> "Settings":
        env = os.environ.get
        return cls(
            database_url=env("DATABASE_URL", cls.database_url),
            ollama_url=env("OLLAMA_URL", cls.ollama_url),
            ollama_model=env("OLLAMA_MODEL", cls.ollama_model),
            classifier=env("CLASSIFIER", cls.classifier),
            port=int(env("PORT", cls.port)),
        )

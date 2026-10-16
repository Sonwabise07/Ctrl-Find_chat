import logging

from .api import create_server
from .app import build_service
from .settings import Settings


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = Settings.from_env()
    server = create_server(build_service(settings), settings.port)
    logging.info("Data assistant on http://localhost:%s (classifier=%s)", settings.port, settings.classifier)
    server.serve_forever()


if __name__ == "__main__":
    main()

"""Integration tests call the HTTP API, so the same checks can run against another implementation.

Set ASSISTANT_URL to test a running server. Otherwise the app is started in-process.
Set ADMIN_DSN to a database user that can read every table (used to compute expected values).
"""

import json
import os
import threading
import urllib.error
import urllib.request
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg
import pytest

from assistant.api import ASK_PATH, create_server
from assistant.app import build_service
from assistant.settings import Settings

ADMIN_DSN = os.environ.get("ADMIN_DSN", "postgresql://hub:hub@localhost/asset_hub")
EXTERNAL_URL = os.environ.get("ASSISTANT_URL")


class Api:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def ask(self, question: str, context: dict | None = None, email: str | None = None) -> dict:
        payload = {"question": question, "context": context, "as": email}
        request = urllib.request.Request(
            self.base_url + ASK_PATH, json.dumps(payload).encode(), {"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request) as response:
            return json.load(response)

    def get(self, path: str):
        """Returns (status code, parsed body) for a GET request."""
        try:
            with urllib.request.urlopen(self.base_url + path) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            return error.code, json.load(error)

    def dashboard(self, dashboard_id: str, email: str | None = None) -> dict:
        query = f"?as={email}" if email else ""
        return self.get(f"/api/dashboards/{dashboard_id}{query}")[1]


def _serve(settings: Settings) -> Api:
    server = create_server(build_service(settings), port=0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return Api(f"http://127.0.0.1:{server.server_address[1]}")


@pytest.fixture(scope="session")
def settings() -> Settings:
    return replace(Settings.from_env(), classifier="rules")


@pytest.fixture(scope="session")
def api(settings) -> Api:
    return Api(EXTERNAL_URL) if EXTERNAL_URL else _serve(settings)


@pytest.fixture(scope="session")
def sql():
    def run(query: str, *params):
        with psycopg.connect(ADMIN_DSN) as connection:
            return connection.execute(query, params or None).fetchall()

    return run


@pytest.fixture
def fake_ollama(settings):
    """Starts a stand-in for Ollama and returns (set_reply, api) for an assistant that uses it."""
    if EXTERNAL_URL:
        pytest.skip("needs the in-process server")
    reply = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            body = json.dumps({"choices": [{"message": {"content": json.dumps(reply)}}]}).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    ollama = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=ollama.serve_forever, daemon=True).start()

    def make(url: str | None = None) -> Api:
        url = url or f"http://127.0.0.1:{ollama.server_address[1]}"
        return _serve(replace(settings, classifier="auto", ollama_url=url))

    def set_reply(value: dict):
        reply.clear()
        reply.update(value)

    yield set_reply, make
    ollama.shutdown()

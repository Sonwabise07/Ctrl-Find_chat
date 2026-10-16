import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .dashboards.service import DashboardService
from .service import AssistantService

log = logging.getLogger(__name__)
WEB_ROOT = Path(__file__).parent.parent / "web"
MAX_BODY_BYTES = 10_000
MAX_QUESTION_LENGTH = 300
ASK_PATH = "/api/assistant/ask"
META_PATH = "/api/assistant/meta"
DASHBOARDS_PATH = "/api/dashboards"
EMPTY_QUESTION = "Ask a question about assets, warranty, audits or losses."
INVALID_REQUEST = "The request could not be read."
SERVER_ERROR = "Something went wrong on our side. Try again."


class ApiHandler(BaseHTTPRequestHandler):
    service: AssistantService
    dashboards: DashboardService
    web_root: Path

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == META_PATH:
            email = parse_qs(url.query).get("as", [None])[0]
            self._run(lambda: self._send_json(200, self.service.meta(email)))
        elif url.path == DASHBOARDS_PATH:
            self._run(lambda: self._send_json(200, self.dashboards.list()))
        elif url.path.startswith(DASHBOARDS_PATH + "/"):
            email = parse_qs(url.query).get("as", [None])[0]
            self._run(lambda: self._dashboard(url.path.removeprefix(DASHBOARDS_PATH + "/"), email))
        elif url.path in ("/", "/index.html"):
            self._send(200, (self.web_root / "index.html").read_bytes(), "text/html; charset=utf-8")
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path == ASK_PATH:
            self._run(self._ask)
        else:
            self._send_json(404, {"error": "not found"})

    def _dashboard(self, dashboard_id: str, email: str | None):
        dashboard = self.dashboards.get(dashboard_id, email)
        if dashboard is None:
            return self._send_json(404, {"error": "not found"})
        self._send_json(200, dashboard)

    def _ask(self):
        length = min(int(self.headers.get("Content-Length", 0)), MAX_BODY_BYTES)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self._send_json(400, {"error": INVALID_REQUEST})
        question = str(body.get("question", "")).strip()[:MAX_QUESTION_LENGTH]
        if not question:
            return self._send_json(400, {"error": EMPTY_QUESTION})
        context = body.get("context")
        context = context if isinstance(context, dict) else None
        self._send_json(200, self.service.ask(question, context, body.get("as")))

    def _run(self, action):
        try:
            action()
        except Exception:
            log.exception("Request failed")
            self._send_json(500, {"error": SERVER_ERROR})

    def _send_json(self, status, payload):
        self._send(status, json.dumps(payload).encode(), "application/json")

    def _send(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def create_server(service: AssistantService, port: int, web_root: Path = WEB_ROOT) -> ThreadingHTTPServer:
    attributes = {"service": service, "dashboards": service.dashboards, "web_root": web_root}
    handler = type("Handler", (ApiHandler,), attributes)
    return ThreadingHTTPServer(("0.0.0.0", port), handler)

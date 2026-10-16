from pathlib import Path

from ..data.database import Database
from ..data.lookups import existing_tables
from ..identity import DemoIdentity
from ..queries.runner import SCOPE_CTE, SQL_DIR, access_params
from .catalog import Dashboard, Widget
from .shapes import shape


class DashboardService:
    def __init__(
        self,
        dashboards: dict[str, Dashboard],
        database: Database,
        identity: DemoIdentity,
        sql_dir: Path = SQL_DIR,
    ):
        self.dashboards = dashboards
        self.database = database
        self.identity = identity
        self._sql = {
            (dashboard.id, widget.id): SCOPE_CTE + (sql_dir / f"{widget.sql}.sql").read_text()
            for dashboard in dashboards.values()
            for widget in dashboard.widgets
        }

    def list(self) -> list[dict]:
        return [{"id": d.id, "title": d.title} for d in self.dashboards.values()]

    def get(self, dashboard_id: str, email: str | None = None) -> dict | None:
        dashboard = self.dashboards.get(dashboard_id)
        if dashboard is None:
            return None
        with self.database.cursor() as cursor:
            user = self.identity.resolve(cursor, email)
            existing = existing_tables(cursor, dashboard.required_tables)
            widgets = [
                self._widget(cursor, dashboard, widget, user, existing) for widget in dashboard.widgets
            ]
        return {"id": dashboard.id, "title": dashboard.title, "widgets": widgets}

    def widget(self, dashboard_id: str, widget_id: str, email: str | None = None) -> dict | None:
        dashboard = self.dashboards.get(dashboard_id)
        widget = next((w for w in dashboard.widgets if w.id == widget_id), None) if dashboard else None
        if widget is None:
            return None
        with self.database.cursor() as cursor:
            user = self.identity.resolve(cursor, email)
            existing = existing_tables(cursor, set(widget.requires))
            return self._widget(cursor, dashboard, widget, user, existing)

    def _widget(self, cursor, dashboard: Dashboard, widget: Widget, user, existing: set[str]) -> dict:
        head = {"id": widget.id, "type": widget.type, "title": widget.title, "size": widget.size}
        if widget.type == "kpi":
            head["tone"] = widget.tone
        if not set(widget.requires) <= existing:
            return {**head, "available": False, "data": None}
        cursor.execute(self._sql[(dashboard.id, widget.id)], access_params(user))
        return {**head, "available": True, "data": shape(widget, cursor.fetchall())}

from dataclasses import dataclass

SEES_EVERYTHING = {"fixed_assets", "admin"}


@dataclass(frozen=True)
class CurrentUser:
    id: int
    name: str
    role: str
    department_id: int | None = None

    @property
    def sees_everything(self) -> bool:
        return self.role in SEES_EVERYTHING

    @property
    def scope_department_id(self) -> int | None:
        return self.department_id if self.role == "manager" else None


class DemoIdentity:
    """Stands in for the main system's login. Replace with an implementation that reads the token."""

    DEFAULT_EMAIL = "naledi.mokoena@example.co.za"
    ROLES = {
        "naledi.mokoena@example.co.za": "fixed_assets",
        "sipho.dlamini@example.co.za": "manager",
    }

    def resolve(self, cursor, email: str | None = None) -> CurrentUser:
        email = (email or self.DEFAULT_EMAIL).lower()
        cursor.execute(
            """SELECT user_id, department_id, first_name || ' ' || last_name AS name
               FROM asset_management.users WHERE lower(email) = %s""",
            (email,),
        )
        row = cursor.fetchone()
        role = self.ROLES.get(email, "employee")
        if row is None:
            return CurrentUser(id=0, name="Guest", role=role)
        return CurrentUser(row["user_id"], row["name"], role, row["department_id"])

import psycopg
import pytest

S = "asset_management."


def registered(reply: dict) -> int:
    return int(reply["answer"].split("**")[1].split()[0])


def test_employee_sees_only_their_own_assets(api, sql):
    reply = api.ask("How many assets are registered?", email="thandi.nkosi@example.co.za")
    expected = sql(
        f"""SELECT count(*) FROM {S}assets a JOIN {S}users u ON u.user_id = a.assigned_to_user_id
            WHERE u.first_name = 'Thandi'"""
    )[0][0]
    assert registered(reply) == expected


def test_manager_sees_their_department(api, sql):
    reply = api.ask("How many assets are registered?", email="sipho.dlamini@example.co.za")
    expected = sql(
        f"""SELECT count(*) FROM {S}assets
            WHERE department_id = (SELECT department_id FROM {S}users WHERE first_name = 'Sipho')
               OR assigned_to_user_id = (SELECT user_id FROM {S}users WHERE first_name = 'Sipho')"""
    )[0][0]
    assert registered(reply) == expected


def test_fixed_assets_sees_everything(api, sql):
    reply = api.ask("How many assets are registered?")
    assert registered(reply) == sql(f"SELECT count(*) FROM {S}assets")[0][0]


def test_database_role_cannot_write(settings):
    with psycopg.connect(settings.database_url) as connection, pytest.raises(psycopg.errors.Error):
        connection.execute(f"DELETE FROM {S}assets")

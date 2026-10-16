from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


class Database:
    def __init__(self, url: str):
        self.url = url

    @contextmanager
    def cursor(self) -> Iterator[psycopg.Cursor]:
        with (
            psycopg.connect(self.url, row_factory=dict_row, autocommit=True) as connection,
            connection.cursor() as cursor,
        ):
            yield cursor

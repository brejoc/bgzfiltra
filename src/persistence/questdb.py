import typing
import psycopg2 as pg

from datetime import datetime


class QuestDB:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, db_config: typing.Dict):
        """
        Establishing connection to QuestDB.
        """
        self.connection = pg.connect(**db_config)
        self.cursor = self.connection.cursor()

    def setup_tables(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bugs_per_status (product symbol, status symbol, bugs double, created_at timestamp) timestamp(created_at)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bugs_per_component (product symbol, component symbol, bugs double, created_at timestamp) timestamp(created_at)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bugs_l3 (product symbol, status symbol, bugs double, created_at timestamp) timestamp(created_at)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bugs_l3_cases (product symbol, status symbol, bugs double, created_at timestamp) timestamp(created_at)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bugs_priority (product symbol, priority symbol, bugs double, created_at timestamp) timestamp(created_at)"
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS bugs_assigned (product symbol, email symbol, bugs double, created_at timestamp) timestamp(created_at)"
        )

    def insert_status(self, product: str, status: str, count: int, time: datetime):
        self.cursor.execute(
            """
            INSERT INTO bugs_per_status VALUES (%s, %s, %s, %s);""",
            (product, status, count, time),
        )
        self.connection.commit()

    def insert_component(
        self, product: str, component: str, count: int, time: datetime
    ):
        self.cursor.execute(
            """
            INSERT INTO bugs_per_component VALUES (%s, %s, %s, %s);""",
            (product, component, count, time),
        )
        self.connection.commit()

    def insert_l3(self, product: str, status: str, count: int, time: datetime):
        self.cursor.execute(
            """
            INSERT INTO bugs_l3 VALUES (%s, %s, %s, %s);""",
            (product, status, count, time),
        )
        self.connection.commit()

    def insert_l3_cases(self, product: str, status: str, count: int, time: datetime):
        self.cursor.execute(
            """
            INSERT INTO bugs_l3_cases VALUES (%s, %s, %s, %s);""",
            (product, status, count, time),
        )
        self.connection.commit()

    def insert_priority(self, product: str, priority: str, count: int, time: datetime):
        self.cursor.execute(
            """
            INSERT INTO bugs_priority VALUES (%s, %s, %s, %s);""",
            (product, priority, count, time),
        )
        self.connection.commit()

    def insert_assigned(self, product: str, email: str, count: int, time: datetime):
        self.cursor.execute(
            """
            INSERT INTO bugs_assigned VALUES (%s, %s, %s, %s);""",
            (product, email, count, time),
        )
        self.connection.commit()

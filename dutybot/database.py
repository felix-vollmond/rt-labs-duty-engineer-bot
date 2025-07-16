import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv('DB_PATH', 'db/dutybot.sqlite')


class DutyBotDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


    def close(self) -> None:
        self.con.close()

    def load_schema(
            self,
            schema_path: str = 'dutybot/database/schema.sql'
    ) -> None:
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.con.executescript(f.read())
        self.con.commit()


    def get_departments(self) -> list[tuple[int, str]]:
        query = """
            SELECT department_id, name FROM departments
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_department(self, id: int) -> tuple[int, str]:
        query = """
            SELECT department_id, name
            FROM departments
            WHERE department_id = ?
        """
        self.cur.execute(query, (id,))
        return self.cur.fetchone()

    def add_department(self, name: str) -> None:
        query = """
            INSERT INTO departments (name) VALUES (?)
        """
        self.cur.execute(query, (name,))
        self.con.commit()

    def update_department(self, id: int, name: str) -> None:
        query = """
            UPDATE departments SET name = ? WHERE department_id = ?
        """
        self.cur.execute(query, (name, id))
        self.con.commit()

    def delete_department(self, id: int) -> None:
        query = """
            DELETE FROM departments WHERE department_id = ?
        """
        self.cur.execute(query, (id,))
        self.con.commit()

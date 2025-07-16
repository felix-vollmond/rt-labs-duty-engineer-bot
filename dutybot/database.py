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


    def get_engineers(self) -> list[tuple[int, str, str, str, int]]:
        query = """
            SELECT engineer_id,
                   full_name,
                   email,
                   phone,
                   department_id
              FROM engineers
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def get_engineer(self, id: int) -> tuple[int, str, str, str, int]:
        query = """
            SELECT engineer_id,
                   full_name,
                   email,
                   phone,
                   department_id
              FROM engineers
             WHERE engineer_id = ?
        """
        self.cur.execute(query, (id,))
        return self.cur.fetchone()

    def add_engineer(
            self,
            full_name: str,
            department_id: int,
            email: str | None = None,
            phone: str | None = None
    ) -> None:
        query = """
            INSERT INTO engineers (full_name, department_id, email, phone)
            VALUES (?, ?, ?, ?)
        """
        self.cur.execute(query, (full_name, department_id, email, phone))
        self.con.commit()

    def update_engineer(
            self,
            engineer_id: int,
            full_name: str | None = None,
            department_id: int | None = None,
            email: str | None = None,
            phone: str | None = None
    ) -> None:
        fields = []
        values = []

        if full_name is not None:
            fields.append("full_name = ?")
            values.append(full_name)

        if department_id is not None:
            fields.append("department_id = ?")
            values.append(department_id)

        if email is not None:
            fields.append("email = ?")
            values.append(email)

        if phone is not None:
            fields.append("phone = ?")
            values.append(phone)

        if not fields:
            return

        values.append(engineer_id)

        query = f"""
            UPDATE engineers
               SET {', '.join(fields)}
             WHERE engineer_id = ?
        """
        self.cur.execute(query, values)
        self.con.commit()

    def delete_engineer(self, id: int) -> None:
        query = """
            DELETE FROM engineers WHERE engineer_id = ?
        """
        self.cur.execute(query, (id,))
        self.con.commit()

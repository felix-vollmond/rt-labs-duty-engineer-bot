import sqlite3

from dutybot.config import DB_PATH


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


    def get_duties_by_date(self, date: str) -> list[tuple]:
        query = """
            SELECT date,
                   engineer_id,
                   department_id
              FROM duties
             WHERE date = ?
        """
        self.cur.execute(query, (date,))
        return self.cur.fetchall()

    def add_duty(self, date: str, engineer_id: int) -> None:
        query1 = """
            SELECT department_id FROM engineers WHERE engineer_id = ?
        """
        self.cur.execute(query1, (engineer_id,))

        department_id = self.cur.fetchone()[0]

        query2 = """
            INSERT INTO duties (date, engineer_id, department_id)
            VALUES (?, ?, ?)
        """
        self.cur.execute(query2, (date, engineer_id, department_id))
        self.con.commit()

    def update_duty(
            self,
            date: str,
            department_id: int,
            engineer_id: int
    ) -> None:
        if not self.__engineer_in_department(engineer_id, department_id):
            return

        query = """
            UPDATE duties SET engineer_id = ?
            WHERE date = ? AND department_id = ?
        """
        self.cur.execute(query, (engineer_id, date, department_id))
        self.con.commit()

    def delete_duty(self, date: str, department_id: int) -> None:
        query = """
            DELETE FROM duties WHERE date = ? AND department_id = ?
        """
        self.cur.execute(query, (date, department_id))
        self.con.commit()


    def __engineer_in_department(
            self,
            engineer_id: int,
            department_id: int
    ) -> bool:
        query = """
            SELECT 1 FROM engineers
            WHERE engineer_id = ? AND department_id = ?
        """
        self.cur.execute(query, (engineer_id, department_id))
        return self.cur.fetchone() is not None

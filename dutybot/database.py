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

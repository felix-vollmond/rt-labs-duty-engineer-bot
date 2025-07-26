import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_PATH = os.getenv('DB_PATH', 'db/dutybot.sqlite')
ALLOWED_USER_IDS = [
    int(user_id) for user_id
    in os.getenv('ALLOWED_USER_IDS', '').split(',')
    if user_id.strip()
]

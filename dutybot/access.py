from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from dutybot.config import ALLOWED_USER_IDS


def is_user_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS


def restrict_access(handler_func):
    @wraps(handler_func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if not is_user_allowed(user_id):
            if update.message:
                await update.message.reply_text("🚫 Доступ запрещён")
            return
        return await handler_func(update, context)
    return wrapper

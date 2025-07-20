from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        '<b>Дежурный инженер АО «РТ Лабс»</b>\n\n'
        'Этот бот помогает управлять сотрудниками, '
        'отделами и дежурствами.\n\n'
        '<b>Доступные функции:</b>\n'
        '👥 Просмотр, редактирование и удаление сотрудников\n'
        '🏢 Просмотр, редактирование и удаление отделов\n'
        '📅 Назначение и изменение дежурств\n\n'
        '💡 Введите <code>/help</code> для просмотра команд.'
    )
    await update.message.reply_text(text, parse_mode='HTML')


start_handler = CommandHandler('start', start_command)

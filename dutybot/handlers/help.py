from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        '<b>Список команд:</b>\n\n'
        '<code>/start</code> — запуск бота\n'
        '<code>/help</code> — справка по командам\n'
        '<code>/cancel</code> — отмена действия\n'
        '<code>/skip</code> — пропуск поля\n\n'
        '<code>/engineers</code> — список инженеров\n'
        '<code>/newengineer</code> — добавление нового инженера\n\n'
        '<code>/duty</code> — просмотр дежурства за выбранную дату\n'
        '<code>/upcoming</code> — список предстоящих дежурств\n\n'
        '<i>Остальные команды добавятся позже!</i>'
    )
    await update.message.reply_text(text, parse_mode='HTML')


help_handler = CommandHandler('help', help_command)

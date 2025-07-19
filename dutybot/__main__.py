from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes
from dutybot.database import DutyBotDatabase
from dutybot.config import BOT_TOKEN


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


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        '<b>Список команд:</b>\n\n'
        '<code>/start</code> — запуск бота\n'
        '<code>/help</code> — справка по командам\n\n'
        '<i>Остальные команды добавятся позже!</i>'
    )
    await update.message.reply_text(text, parse_mode='HTML')


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Обновление {update} вызвало ошибку {context.error}')


async def on_startup(app: Application):
    commands = [
        BotCommand('start', 'запуск бота'),
        BotCommand('help', 'справка по командам'),
    ]
    await app.bot.set_my_commands(commands)


async def on_shutdown(app: Application) -> None:
    db = app.bot_data.get('db')
    if db: db.close()


def main() -> None:
    app = Application.builder() \
                     .token(BOT_TOKEN) \
                     .post_init(on_startup) \
                     .post_shutdown(on_shutdown) \
                     .build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    app.add_error_handler(error)

    app.bot_data['db'] = DutyBotDatabase()

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

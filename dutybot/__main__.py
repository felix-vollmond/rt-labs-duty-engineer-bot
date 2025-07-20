from telegram import Update, BotCommand
from telegram.ext import Application, ContextTypes

from dutybot.database import DutyBotDatabase
from dutybot.config import BOT_TOKEN

from dutybot.handlers.start import start_handler
from dutybot.handlers.help import help_handler


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

    app.add_handler(start_handler)
    app.add_handler(help_handler)

    app.add_error_handler(error)

    app.bot_data['db'] = DutyBotDatabase()

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

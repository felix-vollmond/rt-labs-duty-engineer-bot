from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, filters
)

from dutybot.database import DutyBotDatabase


NAME, EMAIL, PHONE, DEPARTMENT = range(4)


async def new_engineer_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        '🆕 Создание записи о сотруднике',
        parse_mode='HTML'
    )
    await update.message.reply_text(
        '<i>Полное имя:</i>',
        parse_mode='HTML'
    )
    return NAME


async def name_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        '<i>Адрес электронной почты:</i>',
        parse_mode='HTML'
    )
    return EMAIL


async def email_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        '<i>Номер телефона:</i>',
        parse_mode='HTML'
    )
    return PHONE


async def phone_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        '<i>Департамент:</i>',
        parse_mode='HTML'
    )
    return DEPARTMENT


async def department_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        '✅ Запись создана',
        parse_mode='HTML'
    )
    return ConversationHandler.END


async def skip_email(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        '<i>Номер телефона:</i>',
        parse_mode='HTML'
    )
    return PHONE


async def skip_phone(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        '<i>Департамент:</i>',
        parse_mode='HTML'
    )
    return DEPARTMENT


async def cancel_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text('ℹ️ Создание отменено')
    return ConversationHandler.END


create_engineer_handler = ConversationHandler(
    entry_points=[CommandHandler('newengineer', new_engineer_command)],
    states={
        NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                name_input
            ),
        ],
        EMAIL: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                email_input
            ),
            CommandHandler('skip', skip_email),
        ],
        PHONE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                phone_input
            ),
            CommandHandler('skip', skip_phone),
        ],
        DEPARTMENT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                department_input
            ),
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
)

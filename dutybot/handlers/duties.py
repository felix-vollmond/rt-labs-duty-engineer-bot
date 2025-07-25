import re

from datetime import datetime

from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CommandHandler, MessageHandler, filters
)

from dutybot.database import DutyBotDatabase


DATE = 0

DATE_REGEX = re.compile(r'^\d{2}\.\d{2}\.\d{4}$')


async def duty_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        '📅 <i>Введите дату дежурства в формате <b>ДД.ММ.ГГГГ</b>:</i>',
        parse_mode='HTML'
    )
    return DATE


async def date_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    value = update.message.text.strip()

    if not DATE_REGEX.match(value):
        await update.message.reply_text(
            '❌ Неверный формат. Введите дату как <b>ДД.ММ.ГГГГ</b>:',
            parse_mode='HTML'
        )
        return DATE

    try:
        parsed_date = datetime.strptime(value, '%d.%m.%Y')
    except ValueError:
        await update.message.reply_text(
            '❌ Несуществующая дата. Введите другую:'
        )
        return DATE

    db: DutyBotDatabase = context.bot_data['db']

    iso_date = parsed_date.strftime('%Y-%m-%d')
    duties = db.get_duties_by_date(iso_date)

    text = f'📅 <b>{value}</b>'
    if len(duties) == 0:
        text += '\n\nНа эту дату не назначено ни одного дежурного.'

    keyboard = []

    for _, engineer_id, department_id in duties:
        engineer_name = db.get_engineer(engineer_id)[1]
        department = db.get_department(department_id)[1]

        keyboard.append([
            InlineKeyboardButton(
                f'{engineer_name} | {department}',
                callback_data=f'duty:{iso_date}:{engineer_id}:{department_id}'
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            '➕ Добавить',
            callback_data=f'add_duty:{iso_date}'
        )
    ])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )
    return ConversationHandler.END


duty_command_handler = ConversationHandler(
    entry_points=[CommandHandler('duty', duty_command)],
    states={
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_input)],
    },
    fallbacks=[],
)

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler, ContextTypes, CallbackQueryHandler
)

from dutybot.database import DutyBotDatabase


def get_engineer_buttons(
        context: ContextTypes.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    db: DutyBotDatabase = context.bot_data['db']
    engineers = db.get_engineers()

    keyboard = [
        [InlineKeyboardButton(full_name,
                              callback_data=f'select_engineer:{id}')]
        for id, full_name, *_ in engineers
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


async def engineers_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    reply_markup = get_engineer_buttons(context)

    await update.message.reply_text(
        'Выберите инженера:',
        reply_markup=reply_markup
    )


async def list_engineers(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    reply_markup = get_engineer_buttons(context)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        'Выберите инженера:',
        reply_markup=reply_markup
    )


def engineer_info(db: DutyBotDatabase, engineer_id: int) -> str:
    engineer = db.get_engineer(engineer_id)

    if not engineer:
        return 'Инженер не найден.'

    full_name, email, phone, department_id = engineer[1:]
    department = db.get_department(department_id)[1]
    
    return (
        f'👤 Имя: <b>{full_name}</b>\n\n'
        f'📧 Email: <b>{email}</b>\n\n'
        f'📞 Телефон: <b>{phone}</b>\n\n'
        f'🏢 Отдел: <b>{department}</b>'
    )


async def on_engineer_selected(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    db: DutyBotDatabase = context.bot_data['db']
    engineer_id = int(query.data.split(':')[1])

    text = engineer_info(db, engineer_id)

    keyboard = [
        [
            InlineKeyboardButton(
                '✏️ Редактировать',
                callback_data=f'edit_engineer:{engineer_id}'
            ),
            InlineKeyboardButton(
                '🗑 Удалить',
                callback_data=f'confirm_delete_engineer:{engineer_id}'
            ),
        ],
        [
            InlineKeyboardButton(
                '⬅ Назад',
                callback_data=f'list_engineers'
            ),
        ],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


engineers_command_handler = CommandHandler('engineers', engineers_command)
list_engineers_handler = CallbackQueryHandler(
    list_engineers,
    pattern=r'^list_engineers$'
)
on_engineer_selected_handler = CallbackQueryHandler(
    on_engineer_selected,
    pattern=r'^select_engineer:\d+$'
)

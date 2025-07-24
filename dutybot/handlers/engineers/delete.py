from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, CallbackQueryHandler
)

from dutybot.database import DutyBotDatabase
from .show import get_engineer_buttons


async def on_confirm_delete_engineer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    _, engineer_id = query.data.split(':')
    engineer_id = int(engineer_id)

    keyboard = [
        [
            InlineKeyboardButton(
                '❗ Подтвердить',
                callback_data=f'delete_engineer:{engineer_id}'
            ),
        ],
        [
            InlineKeyboardButton(
                '✖️ Отмена',
                callback_data=f'select_engineer:{engineer_id}'
            ),
        ],
    ]

    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def on_delete_engineer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    _, engineer_id = query.data.split(':')
    engineer_id = int(engineer_id)

    db: DutyBotDatabase = context.bot_data['db']
    department_id = db.get_engineer(engineer_id)[4]
    db.delete_engineer(engineer_id)

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text('🗑 Запись о сотруднике удалена')

    reply_markup = get_engineer_buttons(department_id, context)

    await query.message.reply_text(
        'Выберите инженера:',
        reply_markup=reply_markup
    )


on_confirm_delete_engineer_handler = CallbackQueryHandler(
    on_confirm_delete_engineer,
    pattern=r'^confirm_delete_engineer:\d+$'
)
on_delete_engineer_handler = CallbackQueryHandler(
    on_delete_engineer,
    pattern=r'^delete_engineer:\d+$'
)

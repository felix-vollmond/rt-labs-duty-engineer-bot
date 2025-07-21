from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, CallbackQueryHandler
)


async def on_edit_engineer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    engineer_id = int(query.data.split(':')[1])

    keyboard = [
        [
            InlineKeyboardButton(
                '👤 ФИО',
                callback_data=f'edit_engineer:{engineer_id}:full_name'
            ),
            InlineKeyboardButton(
                '🏢 Отдел',
                callback_data=f'edit_engineer:{engineer_id}:department'
            ),
        ],
        [
            InlineKeyboardButton(
                '📧 Электронная почта',
                callback_data=f'edit_engineer:{engineer_id}:email'
            ),
            InlineKeyboardButton(
                '📞 Телефон',
                callback_data=f'edit_engineer:{engineer_id}:phone'
            ),
        ],
        [
            InlineKeyboardButton(
                '⬅ Назад',
                callback_data=f'select_engineer:{engineer_id}'
            ),
        ],
    ]

    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


on_edit_engineer_handler = CallbackQueryHandler(
    on_edit_engineer,
    pattern=r'^edit_engineer:\d+$'
)

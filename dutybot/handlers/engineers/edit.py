from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)

from dutybot.database import DutyBotDatabase
from .show import engineer_info


(
    EDIT_EMAIL,
    EDIT_PHONE,
    EDIT_NAME,
    EDIT_DEPARTMENT
) = range(4)


def engineer_fields_keyboard(
        engineer_id: int
) -> list[list[InlineKeyboardButton]]:
    return [
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


async def on_edit_engineer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    engineer_id = int(query.data.split(':')[1])

    keyboard = engineer_fields_keyboard(engineer_id)

    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def on_edit_engineer_field(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    _, engineer_id, field = query.data.split(':')
    engineer_id = int(engineer_id)

    context.user_data['edit_engineer'] = {
        'engineer_id': engineer_id,
    }

    prompt = {
        'full_name': 'Введите новое полное имя:',
        'email': 'Введите новый адрес электронной почты:',
        'phone': 'Введите новый номер телефона:',
        'department': 'Выберите отдел из списка:'
    }.get(field)

    await query.edit_message_reply_markup(
        reply_markup=None
    )

    await query.message.reply_text(
        f'<i>{prompt}</i>',
        parse_mode='HTML'
    )

    return {
        'full_name': EDIT_NAME,
        'email': EDIT_EMAIL,
        'phone': EDIT_PHONE,
        'department': EDIT_DEPARTMENT,
    }.get(field)


async def handle_field_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    field: str,
    validator: callable,
    error_text: str,
    success_text: str,
):
    edit_data = context.user_data.get('edit_engineer')
    if not edit_data:
        return

    value = update.message.text.strip()
    engineer_id = edit_data['engineer_id']

    if not validator(value):
        await update.message.reply_text(error_text)
        return

    db: DutyBotDatabase = context.bot_data['db']
    db.update_engineer(engineer_id, **{field: value})

    context.user_data.pop('edit_engineer', None)

    await update.message.reply_text(success_text)

    text = engineer_info(db, engineer_id)
    keyboard = engineer_fields_keyboard(engineer_id)

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def on_email_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_field_input(
        update, context,
        field='email',
        validator=lambda v: bool(v.strip()),  # TODO: implement a real validator
        error_text='❌ Некорректный формат для электронной почты',
        success_text='✅ Электронная почта обновлена',
    )
    return ConversationHandler.END


async def on_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_field_input(
        update, context,
        field='full_name',
        validator=lambda v: bool(v.strip()),
        error_text='❌ Имя не должно быть пустым',
        success_text='✅ Имя обновлено',
    )
    return ConversationHandler.END


async def on_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_field_input(
        update, context,
        field='phone',
        validator=lambda v: bool(v.strip()),  # TODO: implement a real validator
        error_text='❌ Некорректный формат для номера телефона',
        success_text='✅ Номер телефона обновлён',
    )
    return ConversationHandler.END


on_edit_engineer_handler = CallbackQueryHandler(
    on_edit_engineer,
    pattern=r'^edit_engineer:\d+$'
)
edit_conversation_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(
        on_edit_engineer_field,
        pattern=r'^edit_engineer:\d+:(full_name|email|phone|department)$'
    )],
    states={
        EDIT_EMAIL: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            on_email_input
        )],
        EDIT_NAME: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            on_name_input
        )],
        EDIT_PHONE: [MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            on_phone_input
        )],
        EDIT_DEPARTMENT: [],
    },
    fallbacks=[],
)

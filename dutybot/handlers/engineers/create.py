import re

from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
    CommandHandler, MessageHandler, filters
)

from dutybot.database import DutyBotDatabase


EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$')
PHONE_REGEX = re.compile(r'^\+7\d{10}$')

NAME, EMAIL, PHONE, DEPARTMENT = range(4)


async def new_engineer_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data['new_engineer'] = {}

    await update.message.reply_text(
        '🆕 Создание записи о сотруднике',
        parse_mode='HTML'
    )
    await update.message.reply_text(
        '<i>Полное имя:</i>',
        parse_mode='HTML'
    )
    return NAME


def department_keyboard() -> InlineKeyboardMarkup:
    departments = DutyBotDatabase().get_departments()

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            name,
            callback_data=
                f'new_engineer:department:{id}'
        )]
        for id, name in departments
    ])


async def name_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    value = update.message.text.strip()

    context.user_data['new_engineer'].update({
        'full_name': value
    })

    await update.message.reply_text(
        '<i>Адрес электронной почты:</i>',
        parse_mode='HTML'
    )
    return EMAIL


async def email_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    value = update.message.text.strip()

    if not EMAIL_REGEX.match(value):
        await update.message.reply_text(
            '❌ Некорректный формат для электронной почты'
        )
        return EMAIL

    db: DutyBotDatabase = context.bot_data['db']
    if db.email_exists(value):
        await update.message.reply_text(
            '❌ Этот адрес электронной почты занят'
        )
        return EMAIL

    context.user_data['new_engineer'].update({
        'email': value
    })

    await update.message.reply_text(
        '<i>Номер телефона:</i>',
        parse_mode='HTML'
    )
    return PHONE


async def phone_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    value = update.message.text.strip()

    if not PHONE_REGEX.match(value):
        await update.message.reply_text(
            '❌ Некорректный формат для номера телефона'
        )
        return PHONE

    db: DutyBotDatabase = context.bot_data['db']
    if db.phone_exists(value):
        await update.message.reply_text(
            '❌ Этот номер телефона занят'
        )
        return PHONE

    context.user_data['new_engineer'].update({
        'phone': value
    })

    await update.message.reply_text(
        '<i>Выберите департамент из списка:</i>',
        reply_markup=department_keyboard(),
        parse_mode='HTML'
    )
    return DEPARTMENT


async def on_department_selected(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    fields = context.user_data.get('new_engineer')
    context.user_data.pop('new_engineer', None)

    full_name = fields['full_name']
    email = fields['email']
    phone = fields['phone']
    department_id = query.data.split(':')[2]

    db: DutyBotDatabase = context.bot_data['db']
    db.add_engineer(full_name, department_id, email, phone)

    await query.message.reply_text('✅ Запись создана')

    return ConversationHandler.END


async def skip_email(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data['new_engineer'].update({
        'email': None
    })

    await update.message.reply_text(
        '<i>Номер телефона:</i>',
        parse_mode='HTML'
    )
    return PHONE


async def skip_phone(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data['new_engineer'].update({
        'phone': None
    })

    await update.message.reply_text(
        '<i>Выберите департамент из списка:</i>',
        reply_markup=department_keyboard(),
        parse_mode='HTML'
    )
    return DEPARTMENT


async def cancel_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data.pop('new_engineer', None)

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
            CallbackQueryHandler(
                on_department_selected,
                pattern=r'^new_engineer:department:\d+$'
            ),
        ],
    },
    fallbacks=[CommandHandler('cancel', cancel_command)],
)

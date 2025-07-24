from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler, ContextTypes, CallbackQueryHandler
)

from dutybot.database import DutyBotDatabase


def department_keyboard() -> InlineKeyboardMarkup:
    departments = DutyBotDatabase().get_departments()
    sorted_departments = sorted(departments, key=lambda x: x[1])

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            name,
            callback_data=f'list_engineers:{id}'
        )]
        for id, name in sorted_departments
    ])


async def list_departments(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    reply_markup = department_keyboard()

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        'Отделы',
        reply_markup=reply_markup
    )


def get_engineer_buttons(
        department_id: int,
        context: ContextTypes.DEFAULT_TYPE
) -> InlineKeyboardMarkup:
    db: DutyBotDatabase = context.bot_data['db']

    engineers = db.get_engineers_by_department(department_id)
    sorted_engineers = sorted(engineers, key=lambda x: x[1])

    keyboard = [
        [InlineKeyboardButton(full_name,
                              callback_data=f'select_engineer:{id}')]
        for id, full_name, *_ in sorted_engineers
    ]
    keyboard.append([InlineKeyboardButton(
        '⬅ Назад',
        callback_data=f'list_departments'
    )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    return reply_markup


async def engineers_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    reply_markup = department_keyboard()

    await update.message.reply_text(
        'Отделы',
        reply_markup=reply_markup
    )


async def list_engineers(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    db: DutyBotDatabase = context.bot_data['db']

    department_id = query.data.split(':')[1]
    department = db.get_department(department_id)[1]

    reply_markup = get_engineer_buttons(department_id, context)

    await query.edit_message_text(
        f'Отдел <b>«{department}»</b>',
        reply_markup=reply_markup,
        parse_mode='HTML'
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
    department_id = db.get_engineer(engineer_id)[4]

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
                callback_data=f'list_engineers:{department_id}'
            ),
        ],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


engineers_command_handler = CommandHandler('engineers', engineers_command)

list_departments_handler = CallbackQueryHandler(
    list_departments,
    pattern=r'^list_departments$'
)
list_engineers_handler = CallbackQueryHandler(
    list_engineers,
    pattern=r'^list_engineers:\d+$'
)
on_engineer_selected_handler = CallbackQueryHandler(
    on_engineer_selected,
    pattern=r'^select_engineer:\d+$'
)

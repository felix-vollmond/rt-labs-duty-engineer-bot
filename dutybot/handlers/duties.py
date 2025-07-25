import re

from datetime import datetime

from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler,
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


def duties_message(
        date: datetime,
        db: DutyBotDatabase
) -> tuple[str, InlineKeyboardMarkup]:
    iso_date = date.strftime('%Y-%m-%d')
    duties = db.get_duties_by_date(iso_date)

    text = f'📅 <b>{date.strftime('%d.%m.%Y')}</b>'
    if len(duties) == 0:
        text += '\n\nНа эту дату не назначено ни одного дежурного.'

    keyboard = []

    for _, engineer_id, department_id in duties:
        engineer_name = db.get_engineer(engineer_id)[1]
        department = db.get_department(department_id)[1]

        keyboard.append([
            InlineKeyboardButton(
                f'{engineer_name} | {department}',
                callback_data=
                    f'duty_engineer:{engineer_id}:{department_id}:{iso_date}'
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            '➕ Добавить',
            callback_data=f'free_departments:{iso_date}'
        )
    ])

    return (text, InlineKeyboardMarkup(keyboard))


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

    text, markup = duties_message(parsed_date, db)

    await update.message.reply_text(
        text,
        reply_markup=markup,
        parse_mode='HTML'
    )
    return ConversationHandler.END


async def show_free_departments(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    db: DutyBotDatabase = context.bot_data['db']

    iso_date = query.data.split(':')[1]

    all_departments = db.get_departments()
    assigned = {
        department_id for _, _, department_id
        in db.get_duties_by_date(iso_date)
    }

    available_departments = [
        (department_id, name) for department_id, name in all_departments
        if department_id not in assigned
    ]

    date = datetime.strptime(iso_date, '%Y-%m-%d').strftime('%d.%m.%Y')

    text = f'📅 <b>{date}</b>'
    keyboard = []

    if not available_departments:
        text += (
            f'\n\nНа эту дату уже назначены'
            f' дежурные во всех отделах.'
        )
    else:
        text += f'\n\nОтделы:'
        for department_id, name in available_departments:
            keyboard.append([
                InlineKeyboardButton(
                    name,
                    callback_data=f'free_department:{department_id}:{iso_date}'
                )
            ])

    keyboard.append([
        InlineKeyboardButton(
            '⬅ Назад',
            callback_data=f'duty:{iso_date}'
        )
    ])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )


async def duty_main_tab(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    iso_date = query.data.split(':')[1]
    parsed_date = datetime.strptime(iso_date, '%Y-%m-%d')

    db: DutyBotDatabase = context.bot_data['db']

    text, markup = duties_message(parsed_date, db)

    await query.edit_message_text(
        text,
        reply_markup=markup,
        parse_mode='HTML'
    )


async def show_free_department(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    db: DutyBotDatabase = context.bot_data['db']

    department_id, iso_date = query.data.split(':')[1:]

    engineers = db.get_engineers_by_department(department_id)
    sorted_engineers = sorted(engineers, key=lambda x: x[1])

    keyboard = [
        [InlineKeyboardButton(
            full_name,
            callback_data=f'add_duty_engineer:{id}:{iso_date}'
        )]
        for id, full_name, *_ in sorted_engineers
    ]
    keyboard.append([InlineKeyboardButton(
        '⬅ Назад',
        callback_data=f'free_departments:{iso_date}'
    )])

    markup = InlineKeyboardMarkup(keyboard)

    date = datetime.strptime(iso_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    department = db.get_department(department_id)[1]

    await query.edit_message_text(
        f'📅 <b>{date}</b>\n\nОтдел <b>«{department}»</b>',
        reply_markup=markup,
        parse_mode='HTML'
    )


async def add_duty_engineer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    db: DutyBotDatabase = context.bot_data['db']

    engineer_id, iso_date = query.data.split(':')[1:]
    db.add_duty(iso_date, engineer_id)

    text, markup = duties_message(datetime.strptime(iso_date, '%Y-%m-%d'), db)
    await query.edit_message_text(
        text,
        reply_markup=markup,
        parse_mode='HTML'
    )


async def replace_duty_engineer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    db: DutyBotDatabase = context.bot_data['db']

    engineer_id, department_id, iso_date = query.data.split(':')[1:]
    db.update_duty(iso_date, department_id, engineer_id)

    text, markup = duties_message(datetime.strptime(iso_date, '%Y-%m-%d'), db)
    await query.edit_message_text(
        text,
        reply_markup=markup,
        parse_mode='HTML'
    )


async def duty_engineer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    db: DutyBotDatabase = context.bot_data['db']

    engineer_id, department_id, iso_date = query.data.split(':')[1:]

    engineers = db.get_engineers_by_department(department_id)
    engineer = db.get_engineer(engineer_id)

    engineers.remove(engineer)
    sorted_engineers = sorted(engineers, key=lambda x: x[1])

    keyboard = [
        [InlineKeyboardButton(
            full_name,
            callback_data=
                f'replace_duty_engineer:{id}:{department_id}:{iso_date}'
        )] for id, full_name, *_ in sorted_engineers
    ]
    keyboard.append([InlineKeyboardButton(
        '🗑 Удалить',
        callback_data=f'delete_duty_engineer:{department_id}:{iso_date}'
    )])
    keyboard.append([InlineKeyboardButton(
        '⬅ Назад',
        callback_data=f'duty:{iso_date}'
    )])

    markup = InlineKeyboardMarkup(keyboard)

    date = datetime.strptime(iso_date, '%Y-%m-%d').strftime('%d.%m.%Y')
    department = db.get_department(department_id)[1]

    await query.edit_message_text(
        text=(
            f'📅 <b>{date}</b>\n\n'
            f'Отдел: <b>{department}</b>\n'
            f'Дежурный: <b>{engineer[1]}</b>'
        ),
        reply_markup=markup,
        parse_mode='HTML'
    )


async def delete_duty_engineer(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    db: DutyBotDatabase = context.bot_data['db']

    department_id, iso_date = query.data.split(':')[1:]
    db.delete_duty(iso_date, department_id)

    text, markup = duties_message(datetime.strptime(iso_date, '%Y-%m-%d'), db)
    await query.edit_message_text(
        text,
        reply_markup=markup,
        parse_mode='HTML'
    )


duty_command_handler = ConversationHandler(
    entry_points=[CommandHandler('duty', duty_command)],
    states={
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_input)],
    },
    fallbacks=[],
)
show_free_departments_handler = CallbackQueryHandler(
    show_free_departments,
    pattern=r'^free_departments:\d{4}-\d{2}-\d{2}$'
)
duty_main_tab_handler = CallbackQueryHandler(
    duty_main_tab,
    pattern=r'^duty:\d{4}-\d{2}-\d{2}$'
)
show_free_department_handler = CallbackQueryHandler(
    show_free_department,
    pattern=r'^free_department:\d+:\d{4}-\d{2}-\d{2}$'
)
add_duty_engineer_handler = CallbackQueryHandler(
    add_duty_engineer,
    pattern=r'^add_duty_engineer:\d+:\d{4}-\d{2}-\d{2}$'
)
replace_duty_engineer_handler = CallbackQueryHandler(
    replace_duty_engineer,
    pattern=r'^replace_duty_engineer:\d+:\d+:\d{4}-\d{2}-\d{2}$'
)
duty_engineer_handler = CallbackQueryHandler(
    duty_engineer,
    pattern=r'^duty_engineer:\d+:\d+:\d{4}-\d{2}-\d{2}$'
)
delete_duty_engineer_handler = CallbackQueryHandler(
    delete_duty_engineer,
    pattern=r'^delete_duty_engineer:\d+:\d{4}-\d{2}-\d{2}$'
)

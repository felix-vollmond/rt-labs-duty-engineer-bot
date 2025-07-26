from collections import defaultdict
from dutybot.database import DutyBotDatabase

example_data = {
    'Управление инцидентами': [
        ('Иванов Иван', 'ivanov@example.com', '+70000000001'),
        ('Петров Пётр', 'petrov@example.com', '+70000000002'),
        ('Смирнов Сергей', 'smirnov@example.com', '+70000000003'),
        ('Орлов Олег', 'orlov@example.com', '+70000000004'),
        ('Козлов Алексей', 'kozlov@example.com', '+70000000005'),
    ],
    'Инфраструктура': [
        ('Соколов Дмитрий', 'sokolov@example.com', '+70000000006'),
        ('Фёдорова Анна', 'fedorova@example.com', '+70000000007'),
        ('Егоров Максим', 'egorov@example.com', '+70000000008'),
        ('Кузнецова Татьяна', 'kuznetsova@example.com', '+70000000009'),
        ('Павлов Юрий', 'pavlov@example.com', '+70000000010'),
    ],
    'ИТ-контроль': [
        ('Новикова Ирина', 'novikova@example.com', '+70000000011'),
        ('Волков Виктор', 'volkov@example.com', '+70000000012'),
        ('Зайцева Мария', 'zaitseva@example.com', '+70000000013'),
        ('Морозов Николай', 'morozov@example.com', '+70000000014'),
        ('Белова Оксана', 'belova@example.com', '+70000000015'),
    ],
    'Бизнес-технологии': [
        ('Васильев Артём', 'vasilyev@example.com', '+70000000016'),
        ('Михайлова Елена', 'mikhaylova@example.com', '+70000000017'),
        ('Никитин Роман', 'nikitin@example.com', '+70000000018'),
        ('Григорьева Наталья', 'grigorieva@example.com', '+70000000019'),
        ('Медведев Андрей', 'medvedev@example.com', '+70000000020'),
    ],
    'Оперативное техническое управление': [
        ('Панина Светлана', 'panina@example.com', '+70000000021'),
        ('Лебедев Константин', 'lebedev@example.com', '+70000000022'),
        ('Сафонова Ольга', 'safonova@example.com', '+70000000023'),
        ('Тихонов Валентин', 'tikhonov@example.com', '+70000000024'),
        ('Чернова Алиса', 'chernova@example.com', '+70000000025'),
        ('Сидоров Евгений', 'sidorov@example.com', '+70000000026'),
    ],
}

with DutyBotDatabase() as db:
    db.load_schema()

    department_ids = {}
    for department_name in example_data:
        db.add_department(department_name)

    departments = db.get_departments()
    department_ids = {name: id for id, name in departments}

    for department, engineers in example_data.items():
        department_id = department_ids[department]
        for full_name, email, phone in engineers:
            db.add_engineer(full_name, department_id, email, phone)

    engineers = db.get_engineers()

    engineers_by_department = defaultdict(list)
    for engineer_id, *_, department_id in engineers:
        engineers_by_department[department_id].append(engineer_id)

    duty_dates = ['2025-07-20', '2025-08-01', '2025-08-02']

    for date in duty_dates:
        for department_id, engineer_ids in engineers_by_department.items():
            engineer_id = engineer_ids[0]
            db.add_duty(date, engineer_id)

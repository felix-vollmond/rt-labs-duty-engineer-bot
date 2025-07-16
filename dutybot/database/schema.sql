CREATE TABLE IF NOT EXISTS engineers (
    engineer_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    department_id INTEGER NOT NULL REFERENCES departments (department_id)
);

CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS duties (
    duty_id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    engineer_id INTEGER NOT NULL REFERENCES engineers (engineer_id),
    department_id INTEGER NOT NULL REFERENCES departments (department_id),
    UNIQUE (date, department_id)
);

-- Таблица групп студентов
CREATE TABLE IF NOT EXISTS student_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица специальностей
CREATE TABLE IF NOT EXISTS specialties (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица преподавателей
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица организаций
CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица профессиональных модулей
CREATE TABLE IF NOT EXISTS modules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    hours INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица студентов (основная таблица)
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE,
    group_id INTEGER REFERENCES student_groups(id),
    study_form VARCHAR(20) DEFAULT 'очная', -- ДОБАВЛЕНО: форма обучения
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица практик студентов
CREATE TABLE IF NOT EXISTS student_practices (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    specialty_id INTEGER REFERENCES specialties(id),
    module_id INTEGER REFERENCES modules(id),
    teacher_id INTEGER REFERENCES teachers(id),
    organization_id INTEGER REFERENCES organizations(id),
    practice_type VARCHAR(50) DEFAULT 'производственная', -- ДОБАВЛЕНО: тип практики (учебная/производственная)

    -- Учебная практика (если есть)
    study_practice_start_day INTEGER,
    study_practice_start_month VARCHAR(20),
    study_practice_start_year INTEGER,
    study_practice_end_day INTEGER,
    study_practice_end_month VARCHAR(20),
    study_practice_end_year INTEGER,
    study_practice_hours INTEGER,

    -- Производственная практика
    production_practice_start_day INTEGER,
    production_practice_start_month VARCHAR(20),
    production_practice_start_year INTEGER,
    production_practice_end_day INTEGER,
    production_practice_end_month VARCHAR(20),
    production_practice_end_year INTEGER,
    production_practice_hours INTEGER,

    -- Руководитель от организации
    organization_supervisor_name VARCHAR(255), -- ДОБАВЛЕНО: ФИО руководителя от организации
    organization_supervisor_position VARCHAR(255), -- ДОБАВЛЕНО: должность руководителя
    organization_supervisor_phone VARCHAR(50), -- ДОБАВЛЕНО: телефон руководителя

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для ускорения поиска
CREATE INDEX IF NOT EXISTS idx_students_group ON students(group_id);
CREATE INDEX IF NOT EXISTS idx_student_practices_student ON student_practices(student_id);
CREATE INDEX IF NOT EXISTS idx_student_practices_specialty ON student_practices(specialty_id);
CREATE INDEX IF NOT EXISTS idx_student_practices_teacher ON student_practices(teacher_id);
CREATE INDEX IF NOT EXISTS idx_student_practices_organization ON student_practices(organization_id);

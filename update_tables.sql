-- Удаляем существующие таблицы (осторожно, это удалит данные!)
DROP TABLE IF EXISTS student_practices;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS modules;
DROP TABLE IF EXISTS organizations;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS specialties;
DROP TABLE IF EXISTS student_groups;

-- Таблица групп студентов
CREATE TABLE student_groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица специальностей
CREATE TABLE specialties (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица преподавателей
CREATE TABLE teachers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица организаций
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица профессиональных модулей
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) UNIQUE NOT NULL,
    hours INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица студентов
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birth_date DATE,
    group_id INTEGER REFERENCES student_groups(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица практик студентов
CREATE TABLE student_practices (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    specialty_id INTEGER REFERENCES specialties(id),
    module_id INTEGER REFERENCES modules(id),
    teacher_id INTEGER REFERENCES teachers(id),
    organization_id INTEGER REFERENCES organizations(id),
    practice_start_day INTEGER,
    practice_start_month VARCHAR(20),
    practice_start_year INTEGER,
    practice_end_day INTEGER,
    practice_end_month VARCHAR(20),
    practice_end_year INTEGER,
    practice_hours INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для ускорения поиска
CREATE INDEX idx_students_group ON students(group_id);
CREATE INDEX idx_student_practices_student ON student_practices(student_id);
CREATE INDEX idx_student_practices_specialty ON student_practices(specialty_id);
CREATE INDEX idx_student_practices_teacher ON student_practices(teacher_id);
CREATE INDEX idx_student_practices_organization ON student_practices(organization_id);

-- Добавляем группу по умолчанию
INSERT INTO student_groups (name) VALUES ('ИСП23') ON CONFLICT (name) DO NOTHING;

-- Добавляем новые столбцы в существующие таблицы и создаем новые таблицы

-- 1. Добавляем форму обучения в таблицу групп
ALTER TABLE student_groups ADD COLUMN IF NOT EXISTS study_form VARCHAR(50) NOT NULL DEFAULT 'Очная';

-- 2. Создаем таблицу руководителей практической подготовки
CREATE TABLE IF NOT EXISTS practice_leaders (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(200) NOT NULL,
    organization_id INTEGER REFERENCES organizations(id),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Добавляем новые поля в таблицу практик студентов
-- Сначала добавляем столбец для типа практики
ALTER TABLE student_practices ADD COLUMN IF NOT EXISTS practice_type VARCHAR(50) NOT NULL DEFAULT 'Производственная';
-- Добавляем столбец для руководителя практики
ALTER TABLE student_practices ADD COLUMN IF NOT EXISTS practice_leader_id INTEGER REFERENCES practice_leaders(id);

-- 4. Добавляем поля для учебной практики
ALTER TABLE student_practices
ADD COLUMN IF NOT EXISTS study_practice_start_day INTEGER,
ADD COLUMN IF NOT EXISTS study_practice_start_month VARCHAR(20),
ADD COLUMN IF NOT EXISTS study_practice_start_year INTEGER,
ADD COLUMN IF NOT EXISTS study_practice_end_day INTEGER,
ADD COLUMN IF NOT EXISTS study_practice_end_month VARCHAR(20),
ADD COLUMN IF NOT EXISTS study_practice_end_year INTEGER,
ADD COLUMN IF NOT EXISTS study_practice_hours INTEGER;

-- 5. Переименовываем существующие поля для ясности (если нужно)
-- COMMENT ON COLUMN student_practices.practice_start_day IS 'День начала производственной практики';
-- COMMENT ON COLUMN student_practices.practice_end_day IS 'День окончания производственной практики';

-- 6. Создаем индекс для руководителей практики
CREATE INDEX IF NOT EXISTS idx_student_practices_practice_leader ON student_practices(practice_leader_id);

-- 7. Добавляем начальные данные для руководителей практики
INSERT INTO practice_leaders (full_name, position, organization_id) VALUES
('Иванов Иван Иванович', 'Главный инженер', 1),
('Петрова Анна Сергеевна', 'Руководитель отдела разработки', 2),
('Сидоров Алексей Петрович', 'Директор по IT', 3),
('Кузнецова Марина Викторовна', 'Заведующий отделом', 4)
ON CONFLICT DO NOTHING;

-- 8. Обновляем существующие группы с формой обучения по умолчанию
UPDATE student_groups SET study_form = 'Очная' WHERE study_form IS NULL;

-- 9. Обновляем существующие записи практик с типом по умолчанию
UPDATE student_practices SET practice_type = 'Производственная' WHERE practice_type IS NULL;

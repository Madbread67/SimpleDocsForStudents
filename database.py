import psycopg2
from psycopg2 import sql
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Подключение к базе данных"""
        try:
            # Берем параметры из переменных окружения
            db_params = {
                'host': os.environ.get('DB_HOST', 'localhost'),
                'database': os.environ.get('DB_NAME', 'practice_db'),
                'user': os.environ.get('DB_USER', 'postgres'),
                'password': os.environ.get('DB_PASSWORD', ''),
                'port': os.environ.get('DB_PORT', '5432')
            }

            print("Подключение к базе данных...")
            print(f"  Хост: {db_params['host']}")
            print(f"  База: {db_params['database']}")
            print(f"  Пользователь: {db_params['user']}")

            self.connection = psycopg2.connect(**db_params)
            self.connection.autocommit = True
            print("✓ Подключение успешно")

            # Создаем таблицы
            self.create_tables()
            # Загружаем начальные данные
            self.load_initial_data()
            return True

        except psycopg2.OperationalError as e:
            print(f"✗ Ошибка подключения: {e}")
            return False
        except Exception as e:
            print(f"✗ Неизвестная ошибка: {e}")
            return False

    def create_tables(self):
        """Создание нормализованных таблиц"""
        try:
            with self.connection.cursor() as cursor:
                # Таблица групп студентов
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_groups (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        study_form VARCHAR(50) NOT NULL DEFAULT 'Очная',  -- НОВОЕ: Форма обучения
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица специальностей
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS specialties (
                        id SERIAL PRIMARY KEY,
                        code VARCHAR(20) UNIQUE NOT NULL,
                        name VARCHAR(500) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица преподавателей
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS teachers (
                        id SERIAL PRIMARY KEY,
                        full_name VARCHAR(255) NOT NULL,
                        phone VARCHAR(50) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица руководителей практической подготовки (НОВАЯ ТАБЛИЦА)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS practice_leaders (
                        id SERIAL PRIMARY KEY,
                        full_name VARCHAR(255) NOT NULL,
                        position VARCHAR(200) NOT NULL,
                        organization_id INTEGER REFERENCES organizations(id),
                        phone VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица организаций
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS organizations (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(500) UNIQUE NOT NULL,
                        address TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица профессиональных модулей
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS modules (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(500) UNIQUE NOT NULL,
                        hours INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица студентов
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        id SERIAL PRIMARY KEY,
                        full_name VARCHAR(255) NOT NULL,
                        birth_date DATE,
                        group_id INTEGER REFERENCES student_groups(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Таблица практик студентов (ОБНОВЛЕННАЯ)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS student_practices (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
                        specialty_id INTEGER REFERENCES specialties(id),
                        module_id INTEGER REFERENCES modules(id),
                        teacher_id INTEGER REFERENCES teachers(id),
                        organization_id INTEGER REFERENCES organizations(id),
                        practice_leader_id INTEGER REFERENCES practice_leaders(id),  -- НОВОЕ: Руководитель практики
                        practice_type VARCHAR(50) NOT NULL DEFAULT 'Производственная',  -- НОВОЕ: Тип практики

                        -- Производственная практика
                        practice_start_day INTEGER,
                        practice_start_month VARCHAR(20),
                        practice_start_year INTEGER,
                        practice_end_day INTEGER,
                        practice_end_month VARCHAR(20),
                        practice_end_year INTEGER,
                        practice_hours INTEGER,

                        -- Учебная практика (НОВАЯ)
                        study_practice_start_day INTEGER,
                        study_practice_start_month VARCHAR(20),
                        study_practice_start_year INTEGER,
                        study_practice_end_day INTEGER,
                        study_practice_end_month VARCHAR(20),
                        study_practice_end_year INTEGER,
                        study_practice_hours INTEGER,

                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Создаем индексы
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_students_group
                    ON students(group_id)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_student_practices_student
                    ON student_practices(student_id)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_student_practices_practice_leader
                    ON student_practices(practice_leader_id)
                """)

                print("✓ Нормализованные таблицы созданы")

        except Exception as e:
            print(f"✗ Ошибка создания таблиц: {e}")
            raise

    def load_initial_data(self):
        """Загрузка начальных данных в нормализованные таблицы"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, есть ли уже данные
                cursor.execute("SELECT COUNT(*) FROM specialties")
                specialties_count = cursor.fetchone()[0]

                if specialties_count == 0:
                    print("Загрузка начальных данных...")

                    # 1. Добавляем группы по умолчанию с формой обучения
                    groups = [
                        ('ИСП23', 'Очная'),
                        ('ИСП24', 'Очная'),
                        ('ЗИСП23', 'Заочная'),
                    ]

                    for name, study_form in groups:
                        cursor.execute("""
                            INSERT INTO student_groups (name, study_form)
                            VALUES (%s, %s)
                            ON CONFLICT (name) DO NOTHING
                        """, (name, study_form))

                    # 2. Добавляем специальности
                    specialties = [
                        ('09.02.07', '09.02.07 Информационные системы и программирование'),
                        ('09.02.06', '09.02.06 Сетевое и системное администрирование'),
                        ('09.02.05', '09.02.05 Прикладная информатика'),
                    ]

                    for code, name in specialties:
                        cursor.execute("""
                            INSERT INTO specialties (code, name)
                            VALUES (%s, %s)
                            ON CONFLICT (code) DO NOTHING
                        """, (code, name))

                    # 3. Добавляем преподавателей
                    teachers = [
                        ('Тарджиманян Лия Николаевна', '8-915-059-50-47'),
                        ('Истратова Светлана Михайловна', '8-916-305-03-89'),
                        ('Петров Иван Сергеевич', '8-905-123-45-67'),
                        ('Сидорова Мария Владимировна', '8-903-987-65-43'),
                    ]

                    for name, phone in teachers:
                        cursor.execute("""
                            INSERT INTO teachers (full_name, phone)
                            VALUES (%s, %s)
                            ON CONFLICT (full_name) DO NOTHING
                        """, (name, phone))

                    # 4. Добавляем организации
                    organizations = [
                        ('АО "НЦВ Миль и Камов"', 'Московская область, г. Люберцы, ул. Летная, д.1'),
                        ('ООО "ИТ-Компания"', 'г. Москва, ул. Тверская, д.10'),
                        ('ЗАО "Технологии будущего"', 'г. Москва, пр. Мира, д.25'),
                        ('ГБУ "Центр разработки"', 'г. Люберцы, Октябрьский проспект, д.50'),
                    ]

                    for name, address in organizations:
                        cursor.execute("""
                            INSERT INTO organizations (name, address)
                            VALUES (%s, %s)
                            ON CONFLICT (name) DO NOTHING
                        """, (name, address))

                    # 5. Добавляем руководителей практической подготовки
                    cursor.execute("""
                        INSERT INTO practice_leaders (full_name, position, organization_id)
                        VALUES
                        ('Иванов Иван Иванович', 'Главный инженер', 1),
                        ('Петрова Анна Сергеевна', 'Руководитель отдела разработки', 2),
                        ('Сидоров Алексей Петрович', 'Директор по IT', 3),
                        ('Кузнецова Марина Викторовна', 'Заведующий отделом', 4)
                        ON CONFLICT DO NOTHING
                    """)

                    # 6. Добавляем модули
                    modules = [
                        ('ПМ 11 Разработка, администрирование и защита баз данных', 72),
                        ('ПМ 01 Разработка программных модулей', 108),
                        ('ПМ 02 Разработка и администрирование баз данных', 144),
                        ('ПМ 03 Участие в интеграции программных модулей', 72),
                    ]

                    for name, hours in modules:
                        cursor.execute("""
                            INSERT INTO modules (name, hours)
                            VALUES (%s, %s)
                            ON CONFLICT (name) DO NOTHING
                        """, (name, hours))

                    print("✓ Начальные данные загружены")

        except Exception as e:
            print(f"✗ Ошибка загрузки начальных данных: {e}")

    # === МЕТОДЫ ДЛЯ РАБОТЫ С ГРУППАМИ ===

    def get_groups(self):
        """Получение списка групп с формой обучения"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, name, study_form FROM student_groups ORDER BY name")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения групп: {e}")
            return []

    def get_group_details(self, group_id):
        """Получение детальной информации о группе"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, study_form FROM student_groups WHERE id = %s
                """, (group_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'id': result[0],
                        'name': result[1],
                        'study_form': result[2]
                    }
                return None
        except Exception as e:
            print(f"Ошибка получения данных группы: {e}")
            return None

    def add_group(self, group_name, study_form='Очная'):
        """Добавление новой группы"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO student_groups (name, study_form)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (group_name, study_form))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Ошибка добавления группы: {e}")
            return None

    def update_group(self, group_id, new_name, study_form=None):
        """Обновление названия группы и формы обучения"""
        try:
            with self.connection.cursor() as cursor:
                if study_form:
                    cursor.execute("""
                        UPDATE student_groups
                        SET name = %s, study_form = %s
                        WHERE id = %s
                    """, (new_name, study_form, group_id))
                else:
                    cursor.execute("""
                        UPDATE student_groups
                        SET name = %s
                        WHERE id = %s
                    """, (new_name, group_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка обновления группы: {e}")
            return False

    def delete_group(self, group_id):
        """Удаление группы"""
        try:
            with self.connection.cursor() as cursor:
                # Сначала удаляем студентов группы
                cursor.execute("DELETE FROM students WHERE group_id = %s", (group_id,))
                # Затем удаляем саму группу
                cursor.execute("DELETE FROM student_groups WHERE id = %s", (group_id,))
                return True
        except Exception as e:
            print(f"Ошибка удаления группы: {e}")
            return False

    # === МЕТОДЫ ДЛЯ РАБОТЫ СО СПРАВОЧНИКАМИ ===

    def get_specialties(self):
        """Получение списка специальностей"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, code, name FROM specialties ORDER BY code")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения специальностей: {e}")
            return []

    def get_teachers(self):
        """Получение списка преподавателей"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, full_name, phone FROM teachers ORDER BY full_name")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения преподавателей: {e}")
            return []

    def get_practice_leaders(self):
        """Получение списка руководителей практической подготовки"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT pl.id, pl.full_name, pl.position,
                           o.name as organization_name, pl.phone
                    FROM practice_leaders pl
                    LEFT JOIN organizations o ON pl.organization_id = o.id
                    ORDER BY pl.full_name
                """)
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения руководителей практики: {e}")
            return []

    def get_organizations(self):
        """Получение списка организаций"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, name, address FROM organizations ORDER BY name")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения организаций: {e}")
            return []

    def get_modules(self):
        """Получение списка модулей"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT id, name, hours FROM modules ORDER BY name")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения модулей: {e}")
            return []

    def add_practice_leader(self, full_name, position, organization_id, phone=None):
        """Добавление нового руководителя практики"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO practice_leaders (full_name, position, organization_id, phone)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (full_name, position, organization_id, phone))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Ошибка добавления руководителя практики: {e}")
            return None

    def add_teacher(self, full_name, phone):
        """Добавление нового преподавателя"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO teachers (full_name, phone)
                    VALUES (%s, %s)
                    ON CONFLICT (full_name) DO NOTHING
                    RETURNING id
                """, (full_name, phone))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Ошибка добавления преподавателя: {e}")
            return None

    def add_organization(self, name, address):
        """Добавление новой организации"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO organizations (name, address)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                """, (name, address))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Ошибка добавления организации: {e}")
            return None

    # === МЕТОДЫ ДЛЯ РАБОТЫ СО СТУДЕНТАМИ ===

    def get_students_by_group(self, group_id):
        """Получение студентов по группе"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        s.id,
                        s.full_name,
                        TO_CHAR(s.birth_date, 'DD.MM.YYYY') as birth_date,
                        g.name as group_name,
                        g.study_form as study_form
                    FROM students s
                    LEFT JOIN student_groups g ON s.group_id = g.id
                    WHERE s.group_id = %s
                    ORDER BY s.full_name
                """, (group_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения студентов: {e}")
            return []

    def get_student_details(self, student_id):
        """Получение детальной информации о студенте с практикой"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        s.id,
                        s.full_name,
                        s.birth_date,
                        s.group_id,
                        g.name as group_name,
                        g.study_form as study_form,
                        sp.specialty_id,
                        sp.module_id,
                        sp.teacher_id,
                        sp.organization_id,
                        sp.practice_leader_id,
                        sp.practice_type,

                        -- Производственная практика
                        sp.practice_start_day,
                        sp.practice_start_month,
                        sp.practice_start_year,
                        sp.practice_end_day,
                        sp.practice_end_month,
                        sp.practice_end_year,
                        sp.practice_hours,

                        -- Учебная практика
                        sp.study_practice_start_day,
                        sp.study_practice_start_month,
                        sp.study_practice_start_year,
                        sp.study_practice_end_day,
                        sp.study_practice_end_month,
                        sp.study_practice_end_year,
                        sp.study_practice_hours
                    FROM students s
                    LEFT JOIN student_groups g ON s.group_id = g.id
                    LEFT JOIN student_practices sp ON s.id = sp.student_id
                    WHERE s.id = %s
                """, (student_id,))

                result = cursor.fetchone()
                if not result:
                    return None

                # Преобразуем в словарь
                columns = [desc[0] for desc in cursor.description]
                student_data = dict(zip(columns, result))

                # Получаем связанные данные
                if student_data.get('specialty_id'):
                    cursor.execute("SELECT code, name FROM specialties WHERE id = %s",
                                 (student_data['specialty_id'],))
                    specialty = cursor.fetchone()
                    if specialty:
                        student_data['specialty_code'] = specialty[0]
                        student_data['specialty_name'] = specialty[1]

                if student_data.get('module_id'):
                    cursor.execute("SELECT name, hours FROM modules WHERE id = %s",
                                 (student_data['module_id'],))
                    module = cursor.fetchone()
                    if module:
                        student_data['module_name'] = module[0]
                        student_data['module_hours'] = module[1]

                if student_data.get('teacher_id'):
                    cursor.execute("SELECT full_name, phone FROM teachers WHERE id = %s",
                                 (student_data['teacher_id'],))
                    teacher = cursor.fetchone()
                    if teacher:
                        student_data['teacher_name'] = teacher[0]
                        student_data['teacher_phone'] = teacher[1]

                if student_data.get('practice_leader_id'):
                    cursor.execute("""
                        SELECT pl.full_name, pl.position, pl.phone, o.name as org_name
                        FROM practice_leaders pl
                        LEFT JOIN organizations o ON pl.organization_id = o.id
                        WHERE pl.id = %s
                    """, (student_data['practice_leader_id'],))
                    leader = cursor.fetchone()
                    if leader:
                        student_data['practice_leader_name'] = leader[0]
                        student_data['practice_leader_position'] = leader[1]
                        student_data['practice_leader_phone'] = leader[2]
                        student_data['practice_leader_org'] = leader[3]

                if student_data.get('organization_id'):
                    cursor.execute("SELECT name, address FROM organizations WHERE id = %s",
                                 (student_data['organization_id'],))
                    org = cursor.fetchone()
                    if org:
                        student_data['organization_name'] = org[0]
                        student_data['organization_address'] = org[1]

                return student_data

        except Exception as e:
            print(f"Ошибка получения деталей студента: {e}")
            return None

    def add_student(self, student_data):
        """Добавление нового студента"""
        try:
            with self.connection.cursor() as cursor:
                # Добавляем студента
                cursor.execute("""
                    INSERT INTO students (full_name, birth_date, group_id)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (
                    student_data['full_name'],
                    student_data['birth_date'],
                    student_data['group_id']
                ))

                student_id = cursor.fetchone()[0]

                # Если есть данные о практике, добавляем их
                practice_fields = [
                    'specialty_id', 'module_id', 'teacher_id', 'organization_id',
                    'practice_leader_id', 'practice_type',
                    'practice_start_day', 'practice_start_month', 'practice_start_year',
                    'practice_end_day', 'practice_end_month', 'practice_end_year',
                    'practice_hours',
                    'study_practice_start_day', 'study_practice_start_month', 'study_practice_start_year',
                    'study_practice_end_day', 'study_practice_end_month', 'study_practice_end_year',
                    'study_practice_hours'
                ]

                # Проверяем, есть ли хотя бы одно поле практики
                has_practice_data = any(field in student_data for field in practice_fields)

                if has_practice_data:
                    cursor.execute("""
                        INSERT INTO student_practices (
                            student_id, specialty_id, module_id, teacher_id,
                            organization_id, practice_leader_id, practice_type,
                            practice_start_day, practice_start_month, practice_start_year,
                            practice_end_day, practice_end_month, practice_end_year,
                            practice_hours,
                            study_practice_start_day, study_practice_start_month, study_practice_start_year,
                            study_practice_end_day, study_practice_end_month, study_practice_end_year,
                            study_practice_hours
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        student_id,
                        student_data.get('specialty_id'),
                        student_data.get('module_id'),
                        student_data.get('teacher_id'),
                        student_data.get('organization_id'),
                        student_data.get('practice_leader_id'),
                        student_data.get('practice_type', 'Производственная'),
                        student_data.get('practice_start_day', 1),
                        student_data.get('practice_start_month', 'января'),
                        student_data.get('practice_start_year', 2025),
                        student_data.get('practice_end_day', 1),
                        student_data.get('practice_end_month', 'января'),
                        student_data.get('practice_end_year', 2025),
                        student_data.get('practice_hours', 0),
                        student_data.get('study_practice_start_day', 1),
                        student_data.get('study_practice_start_month', 'января'),
                        student_data.get('study_practice_start_year', 2025),
                        student_data.get('study_practice_end_day', 1),
                        student_data.get('study_practice_end_month', 'января'),
                        student_data.get('study_practice_end_year', 2025),
                        student_data.get('study_practice_hours', 0)
                    ))

                return student_id

        except Exception as e:
            print(f"Ошибка добавления студента: {e}")
            return None

    def update_student(self, student_id, student_data):
        """Обновление данных студента"""
        try:
            with self.connection.cursor() as cursor:
                # Обновляем данные студента
                cursor.execute("""
                    UPDATE students
                    SET full_name = %s,
                        birth_date = %s,
                        group_id = %s
                    WHERE id = %s
                """, (
                    student_data['full_name'],
                    student_data['birth_date'],
                    student_data.get('group_id'),
                    student_id
                ))

                # Проверяем, есть ли уже запись о практике
                cursor.execute("SELECT id FROM student_practices WHERE student_id = %s", (student_id,))
                practice_exists = cursor.fetchone()

                if practice_exists:
                    # Обновляем существующую запись
                    cursor.execute("""
                        UPDATE student_practices
                        SET specialty_id = %s,
                            module_id = %s,
                            teacher_id = %s,
                            organization_id = %s,
                            practice_leader_id = %s,
                            practice_type = %s,
                            practice_start_day = %s,
                            practice_start_month = %s,
                            practice_start_year = %s,
                            practice_end_day = %s,
                            practice_end_month = %s,
                            practice_end_year = %s,
                            practice_hours = %s,
                            study_practice_start_day = %s,
                            study_practice_start_month = %s,
                            study_practice_start_year = %s,
                            study_practice_end_day = %s,
                            study_practice_end_month = %s,
                            study_practice_end_year = %s,
                            study_practice_hours = %s
                        WHERE student_id = %s
                    """, (
                        student_data.get('specialty_id'),
                        student_data.get('module_id'),
                        student_data.get('teacher_id'),
                        student_data.get('organization_id'),
                        student_data.get('practice_leader_id'),
                        student_data.get('practice_type', 'Производственная'),
                        student_data.get('practice_start_day', 1),
                        student_data.get('practice_start_month', 'января'),
                        student_data.get('practice_start_year', 2025),
                        student_data.get('practice_end_day', 1),
                        student_data.get('practice_end_month', 'января'),
                        student_data.get('practice_end_year', 2025),
                        student_data.get('practice_hours', 0),
                        student_data.get('study_practice_start_day', 1),
                        student_data.get('study_practice_start_month', 'января'),
                        student_data.get('study_practice_start_year', 2025),
                        student_data.get('study_practice_end_day', 1),
                        student_data.get('study_practice_end_month', 'января'),
                        student_data.get('study_practice_end_year', 2025),
                        student_data.get('study_practice_hours', 0),
                        student_id
                    ))
                else:
                    # Создаем новую запись
                    practice_fields = [
                        'specialty_id', 'module_id', 'teacher_id', 'organization_id',
                        'practice_leader_id', 'practice_type'
                    ]

                    has_practice_data = any(field in student_data for field in practice_fields)

                    if has_practice_data:
                        cursor.execute("""
                            INSERT INTO student_practices (
                                student_id, specialty_id, module_id, teacher_id,
                                organization_id, practice_leader_id, practice_type,
                                practice_start_day, practice_start_month, practice_start_year,
                                practice_end_day, practice_end_month, practice_end_year,
                                practice_hours,
                                study_practice_start_day, study_practice_start_month, study_practice_start_year,
                                study_practice_end_day, study_practice_end_month, study_practice_end_year,
                                study_practice_hours
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            student_id,
                            student_data.get('specialty_id'),
                            student_data.get('module_id'),
                            student_data.get('teacher_id'),
                            student_data.get('organization_id'),
                            student_data.get('practice_leader_id'),
                            student_data.get('practice_type', 'Производственная'),
                            student_data.get('practice_start_day', 1),
                            student_data.get('practice_start_month', 'января'),
                            student_data.get('practice_start_year', 2025),
                            student_data.get('practice_end_day', 1),
                            student_data.get('practice_end_month', 'января'),
                            student_data.get('practice_end_year', 2025),
                            student_data.get('practice_hours', 0),
                            student_data.get('study_practice_start_day', 1),
                            student_data.get('study_practice_start_month', 'января'),
                            student_data.get('study_practice_start_year', 2025),
                            student_data.get('study_practice_end_day', 1),
                            student_data.get('study_practice_end_month', 'января'),
                            student_data.get('study_practice_end_year', 2025),
                            student_data.get('study_practice_hours', 0)
                        ))

                return True

        except Exception as e:
            print(f"Ошибка обновления студента: {e}")
            return False

    def delete_student(self, student_id):
        """Удаление студента"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Ошибка удаления студента: {e}")
            return False

    def get_student_count(self):
        """Получение количества студентов"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM students")
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Ошибка получения количества: {e}")
            return 0

    def import_from_old_structure(self):
        """Импорт данных из старой структуры таблицы practice_summary"""
        try:
            with self.connection.cursor() as cursor:
                # Проверяем, существует ли старая таблица
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'practice_summary'
                    )
                """)
                old_table_exists = cursor.fetchone()[0]

                if not old_table_exists:
                    print("Старая таблица не существует")
                    return False

                # Получаем данные из старой таблицы
                cursor.execute("""
                    SELECT DISTINCT
                        specialty_code,
                        specialty_name
                    FROM practice_summary
                    WHERE specialty_code IS NOT NULL
                """)
                specialties = cursor.fetchall()

                for code, name in specialties:
                    cursor.execute("""
                        INSERT INTO specialties (code, name)
                        VALUES (%s, %s)
                        ON CONFLICT (code) DO NOTHING
                    """, (code, name))

                # Импортируем преподавателей
                cursor.execute("""
                    SELECT DISTINCT
                        teacher_name,
                        teacher_phone
                    FROM practice_summary
                    WHERE teacher_name IS NOT NULL
                """)
                teachers = cursor.fetchall()

                for name, phone in teachers:
                    cursor.execute("""
                        INSERT INTO teachers (full_name, phone)
                        VALUES (%s, %s)
                        ON CONFLICT (full_name) DO NOTHING
                    """, (name, phone))

                # Импортируем организации
                cursor.execute("""
                    SELECT DISTINCT
                        organization_name,
                        organization_address
                    FROM practice_summary
                    WHERE organization_name IS NOT NULL
                """)
                organizations = cursor.fetchall()

                for name, address in organizations:
                    cursor.execute("""
                        INSERT INTO organizations (name, address)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (name, address))

                # Импортируем модули
                cursor.execute("""
                    SELECT DISTINCT
                        module_name
                    FROM practice_summary
                    WHERE module_name IS NOT NULL
                """)
                modules = cursor.fetchall()

                for (module_name,) in modules:
                    cursor.execute("""
                        INSERT INTO modules (name, hours)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO NOTHING
                    """, (module_name, 72))

                print("✓ Данные импортированы из старой структуры")
                return True

        except Exception as e:
            print(f"Ошибка импорта данных: {e}")
            return False

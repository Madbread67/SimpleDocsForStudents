import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_data():
    """Перенос данных из старой структуры в новую нормализованную"""
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'practice_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("Начинаем миграцию данных...")

        # 1. Проверяем существование старой таблицы
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'practice_summary'
            )
        """)
        old_table_exists = cursor.fetchone()[0]

        if not old_table_exists:
            print("Старая таблица practice_summary не найдена.")
            print("Создаем новую структуру без миграции данных.")
            return True

        # 2. Создаем новую структуру (если еще не создана)
        from database import DatabaseManager
        db = DatabaseManager()

        # 3. Импортируем данные из старой структуры
        success = db.import_from_old_structure()

        if success:
            print("✓ Миграция данных завершена успешно")
            print("Теперь вы можете удалить старую таблицу командой:")
            print("  DROP TABLE IF EXISTS practice_summary;")
        else:
            print("✗ Ошибка при миграции данных")

        return success

    except Exception as e:
        print(f"✗ Ошибка миграции: {e}")
        return False

if __name__ == '__main__':
    migrate_data()

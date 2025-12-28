try:
    import PyQt6
    print("✓ PyQt6 установлен")
except ImportError as e:
    print(f"✗ PyQt6 ошибка: {e}")

try:
    import psycopg2
    print("✓ psycopg2 установлен")
except ImportError as e:
    print(f"✗ psycopg2 ошибка: {e}")

try:
    import docx
    print("✓ python-docx установлен")
except ImportError as e:
    print(f"✗ python-docx ошибка: {e}")

try:
    import dotenv
    print("✓ python-dotenv установлен")
except ImportError as e:
    print(f"✗ python-dotenv ошибка: {e}")

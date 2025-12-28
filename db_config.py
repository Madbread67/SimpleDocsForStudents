# db_config.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import psycopg2
import os

class DBConfigWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Подключение к базе данных")
        self.setFixedSize(600, 550)  # УВЕЛИЧЕН РАЗМЕР
        self.setModal(True)

        self.config = {}
        self.init_ui()
        self.load_saved_config()

    def init_ui(self):
        # Создаем основной лейаут
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title = QLabel("Настройки подключения к PostgreSQL")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 5px;
            padding: 0;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Информационное сообщение
        info_label = QLabel("Введите данные для подключения к базе данных")
        info_label.setStyleSheet("""
            color: #888;
            font-size: 13px;
            margin-bottom: 20px;
            padding: 0;
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)

        # Создаем виджет с полосами прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)

        # Контейнер для формы
        form_container = QWidget()
        form_container.setStyleSheet("background-color: transparent;")
        form_layout = QFormLayout(form_container)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Функция для создания полей ввода с увеличенной высотой
        def create_input_field(label_text, placeholder="", is_password=False, default_value=""):
            container = QWidget()
            container.setStyleSheet("background-color: transparent;")
            layout = QHBoxLayout(container)
            layout.setSpacing(15)
            layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(label_text)
            label.setStyleSheet("""
                color: #e0e0e0;
                font-weight: bold;
                font-size: 12pt;
                min-width: 150px;
                padding: 0;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            if is_password:
                input_widget = QLineEdit()
                input_widget.setEchoMode(QLineEdit.EchoMode.Password)
            else:
                input_widget = QLineEdit()

            input_widget.setText(default_value)
            input_widget.setPlaceholderText(placeholder)
            input_widget.setStyleSheet("""
                QLineEdit {
                    background-color: #353535;
                    border: 2px solid #555;
                    border-radius: 8px;
                    padding: 15px;
                    color: #e0e0e0;
                    font-size: 13pt;
                    min-height: 45px;
                    selection-background-color: #555;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                    background-color: #3a3a3a;
                }
                QLineEdit:hover {
                    border: 2px solid #666;
                }
            """)
            input_widget.setMinimumHeight(50)
            input_widget.setMinimumWidth(300)

            layout.addWidget(label)
            layout.addWidget(input_widget, 1)

            return container, input_widget

        # Создаем поля ввода с увеличенными размерами
        self.host_container, self.host_input = create_input_field("Хост:", "localhost", default_value="localhost")
        self.port_container, self.port_input = create_input_field("Порт:", "5432", default_value="5432")
        self.dbname_container, self.dbname_input = create_input_field("База данных:", "practice_db", default_value="practice_db")
        self.user_container, self.user_input = create_input_field("Пользователь:", "postgres", default_value="postgres")
        self.password_container, self.password_input = create_input_field("Пароль:", "введите пароль", True)

        # Добавляем поля в форму
        form_layout.addRow(self.host_container)
        form_layout.addRow(self.port_container)
        form_layout.addRow(self.dbname_container)
        form_layout.addRow(self.user_container)
        form_layout.addRow(self.password_container)

        # Чекбокс "Запомнить настройки"
        self.save_checkbox = QCheckBox("Запомнить настройки")
        self.save_checkbox.setChecked(True)
        self.save_checkbox.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                font-size: 12pt;
                spacing: 10px;
                padding: 15px 0;
            }
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #555;
                background-color: #353535;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #2196F3;
                background-color: #2196F3;
                border-radius: 4px;
            }
        """)
        form_layout.addRow(self.save_checkbox)

        # Статусная метка
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: #888;
            font-style: italic;
            font-size: 12pt;
            min-height: 30px;
            padding: 15px;
            border-radius: 5px;
            background-color: #2a2a2a;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addRow(self.status_label)

        scroll_area.setWidget(form_container)
        main_layout.addWidget(scroll_area, 1)

        # Кнопки с увеличенными размерами
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.test_button = QPushButton("Тест подключения")
        self.test_button.clicked.connect(self.test_connection)
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13pt;
                border: none;
                min-width: 150px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #777;
            }
        """)

        self.connect_button = QPushButton("Подключиться")
        self.connect_button.clicked.connect(self.save_and_connect)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13pt;
                border: none;
                min-width: 150px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #777;
            }
        """)
        self.connect_button.setDefault(True)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 13pt;
                border: none;
                min-width: 120px;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)

        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # Советы
        tips_label = QLabel("Совет: Если база не существует, создайте её командой:\nsudo -u postgres createdb practice_db")
        tips_label.setStyleSheet("""
            color: #FF9800;
            font-size: 11pt;
            padding: 12px;
            background-color: #333;
            border-radius: 6px;
            border-left: 4px solid #FF9800;
        """)
        tips_label.setWordWrap(True)
        tips_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(tips_label)

        # Устанавливаем стиль для всего окна
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
            }
            QLabel {
                color: #e0e0e0;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #353535;
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                min-height: 30px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666;
            }
        """)

    def load_saved_config(self):
        """Загружает сохраненные настройки из файла .env"""
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()

                # Заполняем поля
                self.host_input.setText(self.config.get('DB_HOST', 'localhost'))
                self.port_input.setText(self.config.get('DB_PORT', '5432'))
                self.dbname_input.setText(self.config.get('DB_NAME', 'practice_db'))
                self.user_input.setText(self.config.get('DB_USER', 'postgres'))
                self.password_input.setText(self.config.get('DB_PASSWORD', ''))
        except Exception as e:
            print(f"Ошибка загрузки конфига: {e}")

    def test_connection(self):
        """Тестирует подключение к базе данных"""
        host = self.host_input.text() or "localhost"
        port = self.port_input.text() or "5432"
        dbname = self.dbname_input.text() or "practice_db"
        user = self.user_input.text() or "postgres"
        password = self.password_input.text()

        if not password:
            self.show_status("❌ Введите пароль!", "red")
            return

        # Временно отключаем кнопки
        self.test_button.setEnabled(False)
        self.connect_button.setEnabled(False)
        self.test_button.setText("Подключение...")
        QApplication.processEvents()

        try:
            # Пробуем подключиться
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=dbname,
                user=user,
                password=password,
                connect_timeout=5
            )

            # Проверяем, есть ли нужные таблицы
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]

            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'practice_summary')")
            table_exists = cursor.fetchone()[0]

            conn.close()

            if table_exists:
                self.show_status("✅ Подключение успешно! Таблицы найдены.", "green")
            else:
                self.show_status("✅ Подключение успешно! База данных пуста.", "green")

            # Краткая информация о версии PostgreSQL
            version_short = version.split(',')[0] if ',' in version else version[:50]
            self.status_label.setToolTip(f"PostgreSQL: {version_short}")

        except psycopg2.OperationalError as e:
            error_msg = str(e)
            if "password authentication failed" in error_msg:
                self.show_status("❌ Ошибка: Неверный пароль или пользователь", "red")
            elif "database" in error_msg and "does not exist" in error_msg:
                self.show_status("❌ Ошибка: База данных не существует", "red")
                self.status_label.setToolTip("Создайте база данных: sudo -u postgres createdb practice_db")
            elif "could not connect" in error_msg or "Connection refused" in error_msg:
                self.show_status("❌ Ошибка: Не удалось подключиться к серверу", "red")
                self.status_label.setToolTip("Убедитесь, что PostgreSQL запущен: sudo systemctl status postgresql")
            else:
                self.show_status(f"❌ Ошибка подключения", "red")
                self.status_label.setToolTip(error_msg[:200])
        except Exception as e:
            self.show_status(f"❌ Неизвестная ошибка", "red")
            self.status_label.setToolTip(str(e)[:200])
        finally:
            # Включаем кнопки обратно
            self.test_button.setEnabled(True)
            self.connect_button.setEnabled(True)
            self.test_button.setText("Тест подключения")

    def save_and_connect(self):
        """Сохраняет настройки и закрывает окно"""
        host = self.host_input.text() or "localhost"
        port = self.port_input.text() or "5432"
        dbname = self.dbname_input.text() or "practice_db"
        user = self.user_input.text() or "postgres"
        password = self.password_input.text()

        if not password:
            self.show_status("❌ Введите пароль!", "red")
            return

        # Временно отключаем кнопку
        self.connect_button.setEnabled(False)
        self.connect_button.setText("Проверка...")
        QApplication.processEvents()

        # Проверяем подключение перед сохранением
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=dbname,
                user=user,
                password=password,
                connect_timeout=3
            )
            conn.close()

            self.config = {
                'DB_HOST': host,
                'DB_PORT': port,
                'DB_NAME': dbname,
                'DB_USER': user,
                'DB_PASSWORD': password
            }

            # Сохраняем в файл .env если отмечен чекбокс
            if self.save_checkbox.isChecked():
                try:
                    with open('.env', 'w') as f:
                        f.write("# Настройки подключения к PostgreSQL\n")
                        for key, value in self.config.items():
                            f.write(f"{key}={value}\n")
                    print("Настройки сохранены в .env")
                except Exception as e:
                    print(f"Ошибка сохранения настроек: {e}")

            self.accept()

        except Exception as e:
            reply = QMessageBox.question(
                self, 'Подтверждение',
                f'Не удалось проверить подключение:\n{str(e)[:100]}\n\nВсё равно продолжить?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.config = {
                    'DB_HOST': host,
                    'DB_PORT': port,
                    'DB_NAME': dbname,
                    'DB_USER': user,
                    'DB_PASSWORD': password
                }

                if self.save_checkbox.isChecked():
                    try:
                        with open('.env', 'w') as f:
                            f.write("# Настройки подключения к PostgreSQL\n")
                            for key, value in self.config.items():
                                f.write(f"{key}={value}\n")
                    except:
                        pass

                self.accept()
        finally:
            # Включаем кнопку обратно
            self.connect_button.setEnabled(True)
            self.connect_button.setText("Подключиться")

    def get_config(self):
        """Возвращает конфигурацию подключения"""
        return self.config

    def show_status(self, message, color):
        """Показывает статусное сообщение"""
        colors = {
            "green": "#4CAF50",
            "red": "#f44336",
            "orange": "#FF9800",
            "blue": "#2196F3"
        }
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"""
            color: {colors.get(color, '#666')};
            font-weight: bold;
            padding: 12px;
            background-color: #2a2a2a;
            border-radius: 5px;
            font-size: 12pt;
            min-height: 30px;
            border: 2px solid {colors.get(color, '#555')};
        """)

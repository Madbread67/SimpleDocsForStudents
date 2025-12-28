# backup_manager.py
import os
import sys
import subprocess
import datetime
import shutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class BackupManager(QDialog):
    """Окно управления бэкапами базы данных"""
    def __init__(self, parent=None, db_config=None):
        super().__init__(parent)
        self.parent_window = parent  # Сохраняем ссылку на главное окно
        self.db_config = db_config or {}
        self.setWindowTitle("Управление бэкапами базы данных")
        self.setModal(True)
        self.setMinimumSize(800, 600)  # УВЕЛИЧЕН РАЗМЕР
        self.resize(800, 600)  # Устанавливаем начальный размер
        self.backup_dir = "backups"
        self.init_ui()

        # Создаем директорию для бэкапов если её нет
        os.makedirs(self.backup_dir, exist_ok=True)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)  # Добавляем отступы

        # Заголовок
        title = QLabel("Управление бэкапами базы данных")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2196F3;
            padding: 10px 0;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Информация о подключении
        info_group = QGroupBox("Информация о подключении")
        info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        info_layout = QVBoxLayout()

        self.info_label = QLabel(
            f"База: {self.db_config.get('DB_NAME', 'Не указана')}\n"
            f"Хост: {self.db_config.get('DB_HOST', 'localhost')}\n"
            f"Пользователь: {self.db_config.get('DB_USER', 'postgres')}"
        )
        self.info_label.setStyleSheet("""
            font-family: 'Courier New', monospace;
            padding: 15px;
            background-color: #2d2d2d;
            border-radius: 5px;
            font-size: 12pt;
        """)
        self.info_label.setWordWrap(True)

        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Панель управления бэкапами
        control_panel = QHBoxLayout()
        control_panel.setSpacing(10)

        self.btn_create_backup = QPushButton("💾 Создать бэкап")
        self.btn_create_backup.clicked.connect(self.create_backup)
        self.btn_create_backup.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 12pt;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.btn_restore_backup = QPushButton("🔄 Восстановить")
        self.btn_restore_backup.clicked.connect(self.restore_backup)
        self.btn_restore_backup.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px 20px;
                font-size: 12pt;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        self.btn_delete_backup = QPushButton("🗑️ Удалить")
        self.btn_delete_backup.clicked.connect(self.delete_backup)
        self.btn_delete_backup.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 12px 20px;
                font-size: 12pt;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)

        self.btn_open_folder = QPushButton("📁 Открыть папку")
        self.btn_open_folder.clicked.connect(self.open_backup_folder)
        self.btn_open_folder.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 12px 20px;
                font-size: 12pt;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)

        control_panel.addWidget(self.btn_create_backup)
        control_panel.addWidget(self.btn_restore_backup)
        control_panel.addWidget(self.btn_delete_backup)
        control_panel.addStretch()
        control_panel.addWidget(self.btn_open_folder)

        layout.addLayout(control_panel)

        # Список бэкапов с заголовком
        backup_group = QGroupBox("Список бэкапов")
        backup_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        backup_layout = QVBoxLayout(backup_group)

        # Информация о выборе
        selection_info = QLabel("Двойной щелчок по бэкапу для восстановления")
        selection_info.setStyleSheet("""
            color: #888;
            font-style: italic;
            padding: 5px;
        """)
        backup_layout.addWidget(selection_info)

        self.backup_list = QListWidget()
        self.backup_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.backup_list.itemDoubleClicked.connect(self.restore_backup)
        self.backup_list.setStyleSheet("""
            QListWidget {
                font-family: 'Courier New', monospace;
                font-size: 11pt;
                padding: 5px;
                border: 1px solid #555;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background-color: #555;
            }
        """)
        backup_layout.addWidget(self.backup_list)

        layout.addWidget(backup_group)

        # Статус
        self.status_label = QLabel("Готово")
        self.status_label.setStyleSheet("""
            color: #666;
            font-style: italic;
            padding: 12px;
            background-color: #2d2d2d;
            border-radius: 5px;
            font-size: 11pt;
            border-left: 4px solid #2196F3;
        """)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        buttons.setStyleSheet("""
            QPushButton {
                padding: 10px 25px;
                font-size: 11pt;
                min-width: 100px;
            }
        """)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Загружаем список бэкапов
        self.load_backup_list()

    def load_backup_list(self):
        """Загрузка списка бэкапов"""
        self.backup_list.clear()

        try:
            files = os.listdir(self.backup_dir)
            backup_files = [f for f in files if f.endswith('.backup') or f.endswith('.sql') or f.endswith('.dump') or f.endswith('.gz')]
            backup_files.sort(reverse=True)  # Сначала новые

            for file in backup_files:
                file_path = os.path.join(self.backup_dir, file)
                file_size = os.path.getsize(file_path)
                modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

                item_text = f"{file} | {self.format_size(file_size)} | {modified_time.strftime('%d.%m.%Y %H:%M')}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, file_path)

                # Делаем элементы повыше для удобства
                item.setSizeHint(QSize(100, 40))

                self.backup_list.addItem(item)

            self.status_label.setText(f"Найдено {len(backup_files)} бэкапов")

        except Exception as e:
            self.status_label.setText(f"Ошибка загрузки списка: {str(e)}")

    def format_size(self, size_bytes):
        """Форматирование размера файла"""
        for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} ТБ"

    def create_backup(self):
        """Создание бэкапа базы данных"""
        try:
            # Генерируем имя файла с датой
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"backup_{timestamp}.backup")

            self.status_label.setText("Создание бэкапа...")
            QApplication.processEvents()

            # Команда для создания бэкапа через pg_dump
            cmd = [
                'pg_dump',
                '-h', self.db_config.get('DB_HOST', 'localhost'),
                '-p', self.db_config.get('DB_PORT', '5432'),
                '-U', self.db_config.get('DB_USER', 'postgres'),
                '-d', self.db_config.get('DB_NAME', 'practice_db'),
                '-F', 'c',  # custom format
                '-f', backup_file
            ]

            # Устанавливаем переменную окружения с паролем
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.get('DB_PASSWORD', '')

            # Выполняем команду
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                self.status_label.setText(f"✅ Бэкап создан: {backup_file}")

                # Предлагаем сжать файл
                reply = QMessageBox.question(
                    self, "Сжатие бэкапа",
                    "Хотите сжать бэкап для экономии места?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.compress_backup(backup_file)

                self.load_backup_list()
            else:
                self.status_label.setText(f"❌ Ошибка создания бэкапа: {result.stderr}")

        except FileNotFoundError:
            self.status_label.setText("❌ pg_dump не найден. Установите PostgreSQL client tools.")
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")

    def compress_backup(self, backup_file):
        """Сжатие бэкапа"""
        try:
            import gzip
            compressed_file = backup_file + '.gz'

            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Удаляем несжатый файл
            os.remove(backup_file)
            self.status_label.setText(f"✅ Бэкап сжат: {compressed_file}")

        except Exception as e:
            self.status_label.setText(f"⚠️ Не удалось сжать: {str(e)}")

    def restore_backup(self):
        """Восстановление базы данных из бэкапа"""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Внимание", "Выберите бэкап для восстановления!")
            return

        backup_file = current_item.data(Qt.ItemDataRole.UserRole)

        # Проверяем, сжат ли файл
        if backup_file.endswith('.gz'):
            reply = QMessageBox.question(
                self, "Восстановление",
                f"Восстановить базу данных из бэкапа?\n\n{os.path.basename(backup_file)}\n\n"
                "ВНИМАНИЕ: Все текущие данные будут перезаписаны!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Распаковываем временно
                import tempfile
                import gzip

                with tempfile.NamedTemporaryFile(delete=False, suffix='.backup') as tmp_file:
                    with gzip.open(backup_file, 'rb') as f_in:
                        shutil.copyfileobj(f_in, tmp_file)

                    tmp_path = tmp_file.name
                    self.perform_restore(tmp_path)

                    # Удаляем временный файл
                    os.unlink(tmp_path)
        else:
            reply = QMessageBox.question(
                self, "Восстановление",
                f"Восстановить базу данных из бэкапа?\n\n{os.path.basename(backup_file)}\n\n"
                "ВНИМАНИЕ: Все текущие данные будут перезаписаны!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.perform_restore(backup_file)

    def perform_restore(self, backup_file):
        """Выполнение восстановления из бэкапа"""
        try:
            self.status_label.setText("Восстановление из бэкапа...")
            QApplication.processEvents()

            # Сначала завершаем все подключения к базе
            terminate_cmd = [
                'psql',
                '-h', self.db_config.get('DB_HOST', 'localhost'),
                '-p', self.db_config.get('DB_PORT', '5432'),
                '-U', self.db_config.get('DB_USER', 'postgres'),
                '-d', 'postgres',  # Подключаемся к системной базе
                '-c', f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                      f"FROM pg_stat_activity WHERE pg_stat_activity.datname = "
                      f"'{self.db_config.get('DB_NAME', 'practice_db')}' AND pid <> pg_backend_pid();"
            ]

            # Команда для восстановления через pg_restore
            restore_cmd = [
                'pg_restore',
                '-h', self.db_config.get('DB_HOST', 'localhost'),
                '-p', self.db_config.get('DB_PORT', '5432'),
                '-U', self.db_config.get('DB_USER', 'postgres'),
                '-d', self.db_config.get('DB_NAME', 'practice_db'),
                '--clean',  # Очистить базу перед восстановлением
                '--if-exists',
                backup_file
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config.get('DB_PASSWORD', '')

            # Завершаем подключения
            result1 = subprocess.run(terminate_cmd, env=env, capture_output=True, text=True)

            # Восстанавливаем
            result2 = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)

            if result2.returncode == 0:
                self.status_label.setText("✅ База данных восстановлена!")

                # Уведомляем главное окно о необходимости обновить подключение
                if self.parent_window and hasattr(self.parent_window, 'refresh_database_connection'):
                    self.parent_window.refresh_database_connection()

                QMessageBox.information(self, "Успех",
                    "База данных успешно восстановлена из бэкапа!\n"
                    "Данные обновлены в интерфейсе.")
            else:
                self.status_label.setText(f"❌ Ошибка восстановления: {result2.stderr}")

        except FileNotFoundError:
            self.status_label.setText("❌ pg_restore не найден. Установите PostgreSQL client tools.")
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)}")

    def delete_backup(self):
        """Удаление выбранного бэкапа"""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Внимание", "Выберите бэкап для удаления!")
            return

        backup_file = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Удалить бэкап?\n\n{os.path.basename(backup_file)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(backup_file)
                self.status_label.setText("✅ Бэкап удален")
                self.load_backup_list()
            except Exception as e:
                self.status_label.setText(f"❌ Ошибка удаления: {str(e)}")

    def open_backup_folder(self):
        """Открытие папки с бэкапами"""
        try:
            if sys.platform == "win32":
                os.startfile(self.backup_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", self.backup_dir])
            else:
                subprocess.run(["xdg-open", self.backup_dir])
        except Exception as e:
            self.status_label.setText(f"❌ Не удалось открыть папку: {str(e)}")

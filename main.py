import sys
import os
import datetime
from datetime import datetime as dt
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import psycopg2
from psycopg2 import sql
from database import DatabaseManager
from universal_template_generator import UniversalDocumentGenerator
from styles import dark_style
from db_config import DBConfigWindow
from template_variables import get_all_variable_names, get_variables_by_category
import re
from typing import Dict, Optional, Any

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ КЛАССЫ
# ============================================

class ReferenceManager(QDialog):
    """Окно управления справочниками"""
    def __init__(self, parent=None, db=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Управление справочниками")
        self.setModal(True)
        self.setMinimumSize(1100, 750)  # Увеличили размер
        self.resize(1100, 750)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Вкладки для разных справочников
        self.tab_widget = QTabWidget()

        # Вкладка специальностей
        self.specialties_tab = QWidget()
        self.init_specialties_tab()
        self.tab_widget.addTab(self.specialties_tab, "📚 Специальности")

        # Вкладка преподавателей
        self.teachers_tab = QWidget()
        self.init_teachers_tab()
        self.tab_widget.addTab(self.teachers_tab, "👨‍🏫 Преподаватели")

        # НОВАЯ ВКЛАДКА: Руководители практики
        self.practice_leaders_tab = QWidget()
        self.init_practice_leaders_tab()
        self.tab_widget.addTab(self.practice_leaders_tab, "👔 Руководители практики")

        # Вкладка организаций
        self.organizations_tab = QWidget()
        self.init_organizations_tab()
        self.tab_widget.addTab(self.organizations_tab, "🏢 Организации")

        # Вкладка модулей
        self.modules_tab = QWidget()
        self.init_modules_tab()
        self.tab_widget.addTab(self.modules_tab, "📖 Модули")

        layout.addWidget(self.tab_widget)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def init_specialties_tab(self):
        """Инициализация вкладки специальностей"""
        layout = QVBoxLayout(self.specialties_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Панель управления
        control_panel = QHBoxLayout()

        btn_add = QPushButton("➕ Добавить")
        btn_add.clicked.connect(self.add_specialty)
        btn_add.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_edit = QPushButton("✏️ Редактировать")
        btn_edit.clicked.connect(self.edit_specialty)
        btn_edit.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_delete = QPushButton("🗑️ Удалить")
        btn_delete.clicked.connect(self.delete_specialty)
        btn_delete.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        control_panel.addWidget(btn_add)
        control_panel.addWidget(btn_edit)
        control_panel.addWidget(btn_delete)
        control_panel.addStretch()

        layout.addLayout(control_panel)

        # Таблица специальностей с автоподгонкой ширины колонок
        self.specialties_table = QTableWidget()
        self.specialties_table.setColumnCount(3)
        self.specialties_table.setHorizontalHeaderLabels(["ID", "Код", "Название"])
        self.specialties_table.setAlternatingRowColors(True)
        self.specialties_table.verticalHeader().setVisible(False)
        self.specialties_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.specialties_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Устанавливаем начальные ширины колонок
        self.specialties_table.setColumnWidth(0, 80)   # ID
        self.specialties_table.setColumnWidth(1, 150)  # Код
        self.specialties_table.horizontalHeader().setStretchLastSection(True)  # Растягиваем последнюю колонку

        # Включаем выделение всей строки
        self.specialties_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #555;
            }
            QHeaderView::section {
                padding: 12px;
                font-weight: bold;
                background-color: #3c3c3c;
            }
        """)

        layout.addWidget(self.specialties_table)

        # Загрузка данных
        self.load_specialties()

    def init_teachers_tab(self):
        """Инициализация вкладки преподавателей"""
        layout = QVBoxLayout(self.teachers_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Панель управления
        control_panel = QHBoxLayout()

        btn_add = QPushButton("➕ Добавить")
        btn_add.clicked.connect(self.add_teacher)
        btn_add.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_edit = QPushButton("✏️ Редактировать")
        btn_edit.clicked.connect(self.edit_teacher)
        btn_edit.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_delete = QPushButton("🗑️ Удалить")
        btn_delete.clicked.connect(self.delete_teacher)
        btn_delete.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        control_panel.addWidget(btn_add)
        control_panel.addWidget(btn_edit)
        control_panel.addWidget(btn_delete)
        control_panel.addStretch()

        layout.addLayout(control_panel)

        # Таблица преподавателей
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(3)
        self.teachers_table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон"])
        self.teachers_table.setAlternatingRowColors(True)
        self.teachers_table.verticalHeader().setVisible(False)
        self.teachers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.teachers_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Устанавливаем начальные ширины колонок
        self.teachers_table.setColumnWidth(0, 80)   # ID
        self.teachers_table.setColumnWidth(1, 350)  # ФИО
        self.teachers_table.setColumnWidth(2, 200)  # Телефон

        self.teachers_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #555;
            }
            QHeaderView::section {
                padding: 12px;
                font-weight: bold;
                background-color: #3c3c3c;
            }
        """)

        layout.addWidget(self.teachers_table)

        # Загрузка данных
        self.load_teachers()

    def init_practice_leaders_tab(self):
        """Инициализация вкладки руководителей практики"""
        layout = QVBoxLayout(self.practice_leaders_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Панель управления
        control_panel = QHBoxLayout()

        btn_add = QPushButton("➕ Добавить")
        btn_add.clicked.connect(self.add_practice_leader)
        btn_add.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_edit = QPushButton("✏️ Редактировать")
        btn_edit.clicked.connect(self.edit_practice_leader)
        btn_edit.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_delete = QPushButton("🗑️ Удалить")
        btn_delete.clicked.connect(self.delete_practice_leader)
        btn_delete.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        control_panel.addWidget(btn_add)
        control_panel.addWidget(btn_edit)
        control_panel.addWidget(btn_delete)
        control_panel.addStretch()

        layout.addLayout(control_panel)

        # Таблица руководителей практики
        self.practice_leaders_table = QTableWidget()
        self.practice_leaders_table.setColumnCount(5)
        self.practice_leaders_table.setHorizontalHeaderLabels(["ID", "ФИО", "Должность", "Организация", "Телефон"])
        self.practice_leaders_table.setAlternatingRowColors(True)
        self.practice_leaders_table.verticalHeader().setVisible(False)
        self.practice_leaders_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.practice_leaders_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Устанавливаем начальные ширины колонок
        self.practice_leaders_table.setColumnWidth(0, 80)   # ID
        self.practice_leaders_table.setColumnWidth(1, 250)  # ФИО
        self.practice_leaders_table.setColumnWidth(2, 200)  # Должность
        self.practice_leaders_table.setColumnWidth(3, 250)  # Организация
        self.practice_leaders_table.setColumnWidth(4, 150)  # Телефон

        self.practice_leaders_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #555;
            }
            QHeaderView::section {
                padding: 12px;
                font-weight: bold;
                background-color: #3c3c3c;
            }
        """)

        layout.addWidget(self.practice_leaders_table)

        # Загрузка данных
        self.load_practice_leaders()

    def init_organizations_tab(self):
        """Инициализация вкладки организаций"""
        layout = QVBoxLayout(self.organizations_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Панель управления
        control_panel = QHBoxLayout()

        btn_add = QPushButton("➕ Добавить")
        btn_add.clicked.connect(self.add_organization)
        btn_add.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_edit = QPushButton("✏️ Редактировать")
        btn_edit.clicked.connect(self.edit_organization)
        btn_edit.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_delete = QPushButton("🗑️ Удалить")
        btn_delete.clicked.connect(self.delete_organization)
        btn_delete.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        control_panel.addWidget(btn_add)
        control_panel.addWidget(btn_edit)
        control_panel.addWidget(btn_delete)
        control_panel.addStretch()

        layout.addLayout(control_panel)

        # Таблица организаций
        self.organizations_table = QTableWidget()
        self.organizations_table.setColumnCount(3)
        self.organizations_table.setHorizontalHeaderLabels(["ID", "Название", "Адрес"])
        self.organizations_table.setAlternatingRowColors(True)
        self.organizations_table.verticalHeader().setVisible(False)
        self.organizations_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.organizations_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Устанавливаем начальные ширины колонок
        self.organizations_table.setColumnWidth(0, 80)   # ID
        self.organizations_table.setColumnWidth(1, 300)  # Название
        self.organizations_table.horizontalHeader().setStretchLastSection(True)  # Растягиваем последнюю колонку

        self.organizations_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #555;
            }
            QHeaderView::section {
                padding: 12px;
                font-weight: bold;
                background-color: #3c3c3c;
            }
        """)

        layout.addWidget(self.organizations_table)

        # Загрузка данных
        self.load_organizations()

    def init_modules_tab(self):
        """Инициализация вкладки модулей"""
        layout = QVBoxLayout(self.modules_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Панель управления
        control_panel = QHBoxLayout()

        btn_add = QPushButton("➕ Добавить")
        btn_add.clicked.connect(self.add_module)
        btn_add.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_edit = QPushButton("✏️ Редактировать")
        btn_edit.clicked.connect(self.edit_module)
        btn_edit.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        btn_delete = QPushButton("🗑️ Удалить")
        btn_delete.clicked.connect(self.delete_module)
        btn_delete.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)

        control_panel.addWidget(btn_add)
        control_panel.addWidget(btn_edit)
        control_panel.addWidget(btn_delete)
        control_panel.addStretch()

        layout.addLayout(control_panel)

        # Таблица модулей
        self.modules_table = QTableWidget()
        self.modules_table.setColumnCount(3)
        self.modules_table.setHorizontalHeaderLabels(["ID", "Название", "Часы"])
        self.modules_table.setAlternatingRowColors(True)
        self.modules_table.verticalHeader().setVisible(False)
        self.modules_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.modules_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Устанавливаем начальные ширины колонок
        self.modules_table.setColumnWidth(0, 80)   # ID
        self.modules_table.setColumnWidth(1, 450)  # Название
        self.modules_table.setColumnWidth(2, 100)  # Часы

        self.modules_table.setStyleSheet("""
            QTableWidget {
                font-size: 11pt;
                selection-background-color: #555;
            }
            QHeaderView::section {
                padding: 12px;
                font-weight: bold;
                background-color: #3c3c3c;
            }
        """)

        layout.addWidget(self.modules_table)

        # Загрузка данных
        self.load_modules()

    # === МЕТОДЫ ЗАГРУЗКИ ДАННЫХ ===

    def load_specialties(self):
        """Загрузка специальностей в таблицу"""
        try:
            specialties = self.db.get_specialties()
            self.specialties_table.setRowCount(0)

            for row, (spec_id, code, name) in enumerate(specialties):
                self.specialties_table.insertRow(row)
                self.specialties_table.setItem(row, 0, QTableWidgetItem(str(spec_id)))
                self.specialties_table.setItem(row, 1, QTableWidgetItem(code))
                self.specialties_table.setItem(row, 2, QTableWidgetItem(name))

            # Автоподгонка ширины колонок по содержимому
            self.specialties_table.resizeColumnsToContents()
            # Минимальные ширины колонок
            self.specialties_table.setColumnWidth(0, 80)
            self.specialties_table.setColumnWidth(1, 150)
        except Exception as e:
            print(f"Ошибка загрузки специальностей: {e}")

    def load_teachers(self):
        """Загрузка преподавателей в таблицу"""
        try:
            teachers = self.db.get_teachers()
            self.teachers_table.setRowCount(0)

            for row, (teacher_id, name, phone) in enumerate(teachers):
                self.teachers_table.insertRow(row)
                self.teachers_table.setItem(row, 0, QTableWidgetItem(str(teacher_id)))
                self.teachers_table.setItem(row, 1, QTableWidgetItem(name))
                self.teachers_table.setItem(row, 2, QTableWidgetItem(phone))

            self.teachers_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Ошибка загрузки преподавателей: {e}")

    def load_practice_leaders(self):
        """Загрузка руководителей практики в таблицу"""
        try:
            practice_leaders = self.db.get_practice_leaders()
            self.practice_leaders_table.setRowCount(0)

            for row, (leader_id, full_name, position, org_name, phone) in enumerate(practice_leaders):
                self.practice_leaders_table.insertRow(row)
                self.practice_leaders_table.setItem(row, 0, QTableWidgetItem(str(leader_id)))
                self.practice_leaders_table.setItem(row, 1, QTableWidgetItem(full_name))
                self.practice_leaders_table.setItem(row, 2, QTableWidgetItem(position))
                self.practice_leaders_table.setItem(row, 3, QTableWidgetItem(org_name if org_name else ""))
                self.practice_leaders_table.setItem(row, 4, QTableWidgetItem(phone if phone else ""))

            self.practice_leaders_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Ошибка загрузки руководителей практики: {e}")

    def load_organizations(self):
        """Загрузка организаций в таблицу"""
        try:
            organizations = self.db.get_organizations()
            self.organizations_table.setRowCount(0)

            for row, (org_id, name, address) in enumerate(organizations):
                self.organizations_table.insertRow(row)
                self.organizations_table.setItem(row, 0, QTableWidgetItem(str(org_id)))
                self.organizations_table.setItem(row, 1, QTableWidgetItem(name))
                self.organizations_table.setItem(row, 2, QTableWidgetItem(address))

            self.organizations_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Ошибка загрузки организаций: {e}")

    def load_modules(self):
        """Загрузка модулей в таблицу"""
        try:
            modules = self.db.get_modules()
            self.modules_table.setRowCount(0)

            for row, (module_id, name, hours) in enumerate(modules):
                self.modules_table.insertRow(row)
                self.modules_table.setItem(row, 0, QTableWidgetItem(str(module_id)))
                self.modules_table.setItem(row, 1, QTableWidgetItem(name))
                self.modules_table.setItem(row, 2, QTableWidgetItem(str(hours)))

            self.modules_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Ошибка загрузки модулей: {e}")

    # === МЕТОДЫ ДОБАВЛЕНИЯ ===

    def add_specialty(self):
        """Добавление новой специальности"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить специальность")
        dialog.setFixedSize(500, 150)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        code_edit = QLineEdit()
        code_edit.setPlaceholderText("09.02.07")
        code_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Информационные системы и программирование")
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("Код специальности:", code_edit)
        form_layout.addRow("Название:", name_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if code_edit.text().strip() and name_edit.text().strip():
                try:
                    with self.db.connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO specialties (code, name)
                            VALUES (%s, %s)
                            ON CONFLICT (code) DO NOTHING
                            RETURNING id
                        """, (code_edit.text().strip(), name_edit.text().strip()))

                        if cursor.fetchone():
                            self.load_specialties()
                            QMessageBox.information(self, "Успех", "Специальность добавлена!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось добавить специальность:\n{str(e)}")

    def add_teacher(self):
        """Добавление нового преподавателя"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить преподавателя")
        dialog.setFixedSize(500, 150)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Фамилия Имя Отчество")
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        phone_edit = QLineEdit()
        phone_edit.setPlaceholderText("8-915-123-45-67")
        phone_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("ФИО:", name_edit)
        form_layout.addRow("Телефон:", phone_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip() and phone_edit.text().strip():
                try:
                    with self.db.connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO teachers (full_name, phone)
                            VALUES (%s, %s)
                            ON CONFLICT (full_name) DO NOTHING
                            RETURNING id
                        """, (name_edit.text().strip(), phone_edit.text().strip()))

                        if cursor.fetchone():
                            self.load_teachers()
                            QMessageBox.information(self, "Успех", "Преподаватель добавлен!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось добавить преподавателя:\n{str(e)}")

    def add_practice_leader(self):
        """Добавление нового руководителя практики"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить руководителя практики")
        dialog.setFixedSize(500, 300)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Фамилия Имя Отчество")
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        position_edit = QLineEdit()
        position_edit.setPlaceholderText("Должность")
        position_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        # Комбобокс для организаций
        org_combo = QComboBox()
        org_combo.setStyleSheet("padding: 10px; font-size: 12pt;")
        org_combo.addItem("-- Выберите организацию --", None)

        try:
            organizations = self.db.get_organizations()
            for org_id, name, address in organizations:
                org_combo.addItem(name, org_id)
        except:
            pass

        phone_edit = QLineEdit()
        phone_edit.setPlaceholderText("8-915-123-45-67")
        phone_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("ФИО:", name_edit)
        form_layout.addRow("Должность:", position_edit)
        form_layout.addRow("Организация:", org_combo)
        form_layout.addRow("Телефон:", phone_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip() and position_edit.text().strip() and org_combo.currentData():
                try:
                    leader_id = self.db.add_practice_leader(
                        name_edit.text().strip(),
                        position_edit.text().strip(),
                        org_combo.currentData(),
                        phone_edit.text().strip() if phone_edit.text().strip() else None
                    )
                    if leader_id:
                        self.load_practice_leaders()
                        QMessageBox.information(self, "Успех", "Руководитель практики добавлен!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось добавить руководителя практики:\n{str(e)}")

    def add_organization(self):
        """Добавление новой организации"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить организацию")
        dialog.setFixedSize(500, 200)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Название организации")
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        address_edit = QTextEdit()
        address_edit.setMaximumHeight(80)
        address_edit.setPlaceholderText("Адрес организации")
        address_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Адрес:", address_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip() and address_edit.toPlainText().strip():
                try:
                    with self.db.connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO organizations (name, address)
                            VALUES (%s, %s)
                            ON CONFLICT (name) DO NOTHING
                            RETURNING id
                        """, (name_edit.text().strip(), address_edit.toPlainText().strip()))

                        if cursor.fetchone():
                            self.load_organizations()
                            QMessageBox.information(self, "Успех", "Организация добавлена!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось добавить организацию:\n{str(e)}")

    def add_module(self):
        """Добавление нового модуля"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить модуль")
        dialog.setFixedSize(500, 150)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_edit = QLineEdit()
        name_edit.setPlaceholderText("ПМ 11 Разработка, администрирование и защита баз данных")
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        hours_spin = QSpinBox()
        hours_spin.setRange(1, 500)
        hours_spin.setValue(72)
        hours_spin.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("Название модуля:", name_edit)
        form_layout.addRow("Часы:", hours_spin)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip():
                try:
                    with self.db.connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO modules (name, hours)
                            VALUES (%s, %s)
                            RETURNING id
                        """, (name_edit.text().strip(), hours_spin.value()))

                        if cursor.fetchone():
                            self.load_modules()
                            QMessageBox.information(self, "Успех", "Модуль добавлен!")
                except psycopg2.IntegrityError:
                    QMessageBox.warning(self, "Ошибка", "Модуль с таким названием уже существует!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось добавить модуль:\n{str(e)}")

    # === МЕТОДЫ РЕДАКТИРОВАНИЯ ===

    def edit_specialty(self):
        """Редактирование специальности"""
        current_row = self.specialties_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите специальность для редактирования!")
            return

        spec_id = self.specialties_table.item(current_row, 0).text()
        current_code = self.specialties_table.item(current_row, 1).text()
        current_name = self.specialties_table.item(current_row, 2).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать специальность")
        dialog.setFixedSize(500, 150)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        code_edit = QLineEdit(current_code)
        code_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        name_edit = QLineEdit(current_name)
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("Код специальности:", code_edit)
        form_layout.addRow("Название:", name_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if code_edit.text().strip() and name_edit.text().strip():
                try:
                    with self.db.connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE specialties
                            SET code = %s, name = %s
                            WHERE id = %s
                        """, (code_edit.text().strip(), name_edit.text().strip(), spec_id))

                        self.load_specialties()
                        QMessageBox.information(self, "Успех", "Специальность обновлена!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось обновить специальность:\n{str(e)}")

    def edit_teacher(self):
        """Редактирование преподавателя"""
        current_row = self.teachers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите преподавателя для редактирования!")
            return

        teacher_id = self.teachers_table.item(current_row, 0).text()
        current_name = self.teachers_table.item(current_row, 1).text()
        current_phone = self.teachers_table.item(current_row, 2).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать преподавателя")
        dialog.setFixedSize(500, 150)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_edit = QLineEdit(current_name)
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        phone_edit = QLineEdit(current_phone)
        phone_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("ФИО:", name_edit)
        form_layout.addRow("Телефон:", phone_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip() and phone_edit.text().strip():
                try:
                    with self.db.connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE teachers
                            SET full_name = %s, phone = %s
                            WHERE id = %s
                        """, (name_edit.text().strip(), phone_edit.text().strip(), teacher_id))

                        self.load_teachers()
                        QMessageBox.information(self, "Успех", "Преподаватель обновлен!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось обновить преподавателя:\n{str(e)}")

    def edit_practice_leader(self):
        """Редактирование руководителя практики"""
        current_row = self.practice_leaders_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите руководителя практики для редактирования!")
            return

        leader_id = self.practice_leaders_table.item(current_row, 0).text()
        current_name = self.practice_leaders_table.item(current_row, 1).text()
        current_position = self.practice_leaders_table.item(current_row, 2).text()
        current_org = self.practice_leaders_table.item(current_row, 3).text()
        current_phone = self.practice_leaders_table.item(current_row, 4).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать руководителя практики")
        dialog.setFixedSize(500, 300)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_edit = QLineEdit(current_name)
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        position_edit = QLineEdit(current_position)
        position_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        # Комбобокс для организаций
        org_combo = QComboBox()
        org_combo.setStyleSheet("padding: 10px; font-size: 12pt;")
        org_combo.addItem("-- Выберите организацию --", None)

        try:
            organizations = self.db.get_organizations()
            for org_id, name, address in organizations:
                org_combo.addItem(name, org_id)
                if name == current_org:
                    org_combo.setCurrentText(name)
        except:
            pass

        phone_edit = QLineEdit(current_phone)
        phone_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("ФИО:", name_edit)
        form_layout.addRow("Должность:", position_edit)
        form_layout.addRow("Организация:", org_combo)
        form_layout.addRow("Телефон:", phone_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip() and position_edit.text().strip() and org_combo.currentData():
                try:
                    if self.db.update_practice_leader(
                        leader_id,
                        name_edit.text().strip(),
                        position_edit.text().strip(),
                        org_combo.currentData(),
                        phone_edit.text().strip() if phone_edit.text().strip() else None
                    ):
                        self.load_practice_leaders()
                        QMessageBox.information(self, "Успех", "Руководитель практики обновлен!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось обновить руководителя практики:\n{str(e)}")

    def edit_organization(self):
        """Редактирование организации"""
        current_row = self.organizations_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите организацию для редактирования!")
            return

        org_id = self.organizations_table.item(current_row, 0).text()
        current_name = self.organizations_table.item(current_row, 1).text()
        current_address = self.organizations_table.item(current_row, 2).text()

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать организацию")
        dialog.setFixedSize(500, 200)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_edit = QLineEdit(current_name)
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        address_edit = QTextEdit(current_address)
        address_edit.setMaximumHeight(80)
        address_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("Название:", name_edit)
        form_layout.addRow("Адрес:", address_edit)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip() and address_edit.toPlainText().strip():
                try:
                    with self.db.connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE organizations
                            SET name = %s, address = %s
                            WHERE id = %s
                        """, (name_edit.text().strip(), address_edit.toPlainText().strip(), org_id))

                        self.load_organizations()
                        QMessageBox.information(self, "Успех", "Организация обновлена!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось обновить организацию:\n{str(e)}")

    def edit_module(self):
        """Редактирование модуля"""
        current_row = self.modules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите модуль для редактирования!")
            return

        module_id = self.modules_table.item(current_row, 0).text()
        current_name = self.modules_table.item(current_row, 1).text()
        current_hours = int(self.modules_table.item(current_row, 2).text())

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать модуль")
        dialog.setFixedSize(500, 150)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        name_edit = QLineEdit(current_name)
        name_edit.setStyleSheet("padding: 10px; font-size: 12pt;")

        hours_spin = QSpinBox()
        hours_spin.setRange(1, 500)
        hours_spin.setValue(current_hours)
        hours_spin.setStyleSheet("padding: 10px; font-size: 12pt;")

        form_layout.addRow("Название модуля:", name_edit)
        form_layout.addRow("Часы:", hours_spin)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        layout.addWidget(buttons)

        if dialog.exec():
            if name_edit.text().strip():
                try:
                    with self.db.connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE modules
                            SET name = %s, hours = %s
                            WHERE id = %s
                        """, (name_edit.text().strip(), hours_spin.value(), module_id))

                        self.load_modules()
                        QMessageBox.information(self, "Успех", "Модуль обновлен!")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось обновить модуль:\n{str(e)}")

    # === МЕТОДЫ УДАЛЕНИЯ ===

    def delete_specialty(self):
        """Удаление специальности"""
        current_row = self.specialties_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите специальность для удаления!")
            return

        spec_id = self.specialties_table.item(current_row, 0).text()
        spec_name = self.specialties_table.item(current_row, 2).text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить специальность:\n{spec_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with self.db.connection.cursor() as cursor:
                    cursor.execute("DELETE FROM specialties WHERE id = %s", (spec_id,))
                    self.load_specialties()
                    QMessageBox.information(self, "Успех", "Специальность удалена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить специальность:\n{str(e)}")

    def delete_teacher(self):
        """Удаление преподавателя"""
        current_row = self.teachers_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите преподавателя для удаления!")
            return

        teacher_id = self.teachers_table.item(current_row, 0).text()
        teacher_name = self.teachers_table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить преподавателя:\n{teacher_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with self.db.connection.cursor() as cursor:
                    cursor.execute("DELETE FROM teachers WHERE id = %s", (teacher_id,))
                    self.load_teachers()
                    QMessageBox.information(self, "Успех", "Преподаватель удален!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить преподавателя:\n{str(e)}")

    def delete_practice_leader(self):
        """Удаление руководителя практики"""
        current_row = self.practice_leaders_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите руководителя практики для удаления!")
            return

        leader_id = self.practice_leaders_table.item(current_row, 0).text()
        leader_name = self.practice_leaders_table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить руководителя практики:\n{leader_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db.delete_practice_leader(leader_id):
                    self.load_practice_leaders()
                    QMessageBox.information(self, "Успех", "Руководитель практики удален!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить руководителя практики:\n{str(e)}")

    def delete_organization(self):
        """Удаление организации"""
        current_row = self.organizations_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите организацию для удаления!")
            return

        org_id = self.organizations_table.item(current_row, 0).text()
        org_name = self.organizations_table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить организацию:\n{org_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with self.db.connection.cursor() as cursor:
                    cursor.execute("DELETE FROM organizations WHERE id = %s", (org_id,))
                    self.load_organizations()
                    QMessageBox.information(self, "Успех", "Организация удалена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить организацию:\n{str(e)}")

    def delete_module(self):
        """Удаление модуля"""
        current_row = self.modules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите модуль для удаления!")
            return

        module_id = self.modules_table.item(current_row, 0).text()
        module_name = self.modules_table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить модуль:\n{module_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with self.db.connection.cursor() as cursor:
                    cursor.execute("DELETE FROM modules WHERE id = %s", (module_id,))
                    self.load_modules()
                    QMessageBox.information(self, "Успех", "Модуль удален!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить модуль:\n{str(e)}")


class StudentDialog(QDialog):
    """Диалог добавления/редактирования студента"""
    def __init__(self, parent=None, student_data=None, db=None):
        super().__init__(parent)
        self.student_data = student_data
        self.db = db
        self.setWindowTitle('Новый студент' if not student_data else 'Редактирование студента')
        self.setModal(True)
        self.setFixedSize(750, 700)  # Увеличили размер для новых полей
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel('Добавление нового студента' if not self.student_data else 'Редактирование студента')
        title.setStyleSheet('''
            font-size: 16pt;
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 15px;
            padding: 10px;
        ''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Прокручиваемая область
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(15, 15, 15, 15)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Основные поля
        self.fio_edit = QLineEdit()
        self.fio_edit.setPlaceholderText('Фамилия Имя Отчество')
        self.fio_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 12pt;
                min-height: 40px;
            }
        """)

        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDisplayFormat('dd.MM.yyyy')
        self.birth_date_edit.setDate(QDate.currentDate().addYears(-18))
        self.birth_date_edit.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
        """)

        # Выпадающие списки для справочников
        self.specialty_combo = QComboBox()
        self.specialty_combo.setEditable(False)
        self.specialty_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
        """)

        self.teacher_combo = QComboBox()
        self.teacher_combo.setEditable(False)
        self.teacher_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
        """)
        self.teacher_combo.currentIndexChanged.connect(self.on_teacher_changed)

        self.teacher_phone_edit = QLineEdit()
        self.teacher_phone_edit.setReadOnly(True)
        self.teacher_phone_edit.setPlaceholderText('Телефон автоматически заполнится')
        self.teacher_phone_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 12pt;
                min-height: 40px;
                background-color: #3a3a3a;
            }
        """)

        # НОВОЕ: Комбобокс для руководителя практики
        self.practice_leader_combo = QComboBox()
        self.practice_leader_combo.setEditable(False)
        self.practice_leader_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
        """)
        self.practice_leader_combo.currentIndexChanged.connect(self.on_practice_leader_changed)

        self.practice_leader_position_edit = QLineEdit()
        self.practice_leader_position_edit.setReadOnly(True)
        self.practice_leader_position_edit.setPlaceholderText('Должность автоматически заполнится')
        self.practice_leader_position_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 12pt;
                min-height: 40px;
                background-color: #3a3a3a;
            }
        """)

        self.practice_leader_org_edit = QLineEdit()
        self.practice_leader_org_edit.setReadOnly(True)
        self.practice_leader_org_edit.setPlaceholderText('Организация автоматически заполнится')
        self.practice_leader_org_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 12pt;
                min-height: 40px;
                background-color: #3a3a3a;
            }
        """)

        self.organization_combo = QComboBox()
        self.organization_combo.setEditable(False)
        self.organization_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
        """)
        self.organization_combo.currentIndexChanged.connect(self.on_organization_changed)

        self.organization_address_edit = QTextEdit()
        self.organization_address_edit.setMaximumHeight(80)
        self.organization_address_edit.setReadOnly(True)
        self.organization_address_edit.setPlaceholderText('Адрес автоматически заполнится')
        self.organization_address_edit.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                font-size: 12pt;
                background-color: #3a3a3a;
            }
        """)

        self.module_combo = QComboBox()
        self.module_combo.setEditable(False)
        self.module_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
            QComboBox::drop-down {
                width: 30px;
            }
        """)
        self.module_combo.currentIndexChanged.connect(self.on_module_changed)

        # НОВОЕ: Выбор типа практики
        self.practice_type_combo = QComboBox()
        self.practice_type_combo.addItems(['Производственная', 'Учебная'])
        self.practice_type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
        """)
        self.practice_type_combo.currentIndexChanged.connect(self.on_practice_type_changed)

        # НОВОЕ: Часы практики
        self.practice_hours_edit = QSpinBox()
        self.practice_hours_edit.setRange(1, 500)
        self.practice_hours_edit.setValue(72)
        self.practice_hours_edit.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
        """)

        # НОВОЕ: Часы учебной практики
        self.study_practice_hours_edit = QSpinBox()
        self.study_practice_hours_edit.setRange(1, 500)
        self.study_practice_hours_edit.setValue(36)
        self.study_practice_hours_edit.setStyleSheet("""
            QSpinBox {
                padding: 10px;
                font-size: 12pt;
                min-height: 40px;
            }
        """)

        # Загружаем данные в комбобоксы
        self.load_reference_data()

        # Даты производственной практики
        prod_dates_group = QGroupBox("Производственная практика")
        prod_dates_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        prod_dates_layout = QGridLayout(prod_dates_group)
        prod_dates_layout.setSpacing(10)

        prod_dates_layout.addWidget(QLabel('Начало:'), 0, 0)

        self.practice_start_day_edit = QSpinBox()
        self.practice_start_day_edit.setRange(1, 31)
        self.practice_start_day_edit.setValue(8)
        self.practice_start_day_edit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 60px;
            }
        """)
        prod_dates_layout.addWidget(self.practice_start_day_edit, 0, 1)

        self.practice_start_month_combo = QComboBox()
        self.practice_start_month_combo.addItems(['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                                         'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'])
        self.practice_start_month_combo.setCurrentText('декабря')
        self.practice_start_month_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)
        prod_dates_layout.addWidget(self.practice_start_month_combo, 0, 2)

        self.practice_start_year_edit = QSpinBox()
        self.practice_start_year_edit.setRange(2020, 2030)
        self.practice_start_year_edit.setValue(2025)
        self.practice_start_year_edit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 80px;
            }
        """)
        prod_dates_layout.addWidget(self.practice_start_year_edit, 0, 3)

        prod_dates_layout.addWidget(QLabel('Конец:'), 1, 0)

        self.practice_end_day_edit = QSpinBox()
        self.practice_end_day_edit.setRange(1, 31)
        self.practice_end_day_edit.setValue(21)
        self.practice_end_day_edit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 60px;
            }
        """)
        prod_dates_layout.addWidget(self.practice_end_day_edit, 1, 1)

        self.practice_end_month_combo = QComboBox()
        self.practice_end_month_combo.addItems(['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                                       'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'])
        self.practice_end_month_combo.setCurrentText('декабря')
        self.practice_end_month_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)
        prod_dates_layout.addWidget(self.practice_end_month_combo, 1, 2)

        self.practice_end_year_edit = QSpinBox()
        self.practice_end_year_edit.setRange(2020, 2030)
        self.practice_end_year_edit.setValue(2025)
        self.practice_end_year_edit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 80px;
            }
        """)
        prod_dates_layout.addWidget(self.practice_end_year_edit, 1, 3)

        # НОВОЕ: Даты учебной практики
        study_dates_group = QGroupBox("Учебная практика")
        study_dates_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        study_dates_layout = QGridLayout(study_dates_group)
        study_dates_layout.setSpacing(10)

        study_dates_layout.addWidget(QLabel('Начало:'), 0, 0)

        self.study_practice_start_day_edit = QSpinBox()
        self.study_practice_start_day_edit.setRange(1, 31)
        self.study_practice_start_day_edit.setValue(1)
        self.study_practice_start_day_edit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 60px;
            }
        """)
        study_dates_layout.addWidget(self.study_practice_start_day_edit, 0, 1)

        self.study_practice_start_month_combo = QComboBox()
        self.study_practice_start_month_combo.addItems(['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                                         'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'])
        self.study_practice_start_month_combo.setCurrentText('сентября')
        self.study_practice_start_month_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)
        study_dates_layout.addWidget(self.study_practice_start_month_combo, 0, 2)

        self.study_practice_start_year_edit = QSpinBox()
        self.study_practice_start_year_edit.setRange(2020, 2030)
        self.study_practice_start_year_edit.setValue(2025)
        self.study_practice_start_year_edit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 80px;
            }
        """)
        study_dates_layout.addWidget(self.study_practice_start_year_edit, 0, 3)

        study_dates_layout.addWidget(QLabel('Конец:'), 1, 0)

        self.study_practice_end_day_edit = QSpinBox()
        self.study_practice_end_day_edit.setRange(1, 31)
        self.study_practice_end_day_edit.setValue(30)
        self.study_practice_end_day_edit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 60px;
            }
        """)
        study_dates_layout.addWidget(self.study_practice_end_day_edit, 1, 1)

        self.study_practice_end_month_combo = QComboBox()
        self.study_practice_end_month_combo.addItems(['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                                       'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'])
        self.study_practice_end_month_combo.setCurrentText('октября')
        self.study_practice_end_month_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)
        study_dates_layout.addWidget(self.study_practice_end_month_combo, 1, 2)

        self.study_practice_end_year_edit = QSpinBox()
        self.study_practice_end_year_edit.setRange(2020, 2030)
        self.study_practice_end_year_edit.setValue(2025)
        self.study_practice_end_year_edit.setStyleSheet("""
            QSpinBox {
                padding: 8px;
                font-size: 12pt;
                min-width: 80px;
            }
        """)
        study_dates_layout.addWidget(self.study_practice_end_year_edit, 1, 3)

        # Добавляем поля в форму
        form_layout.addRow('ФИО:', self.fio_edit)
        form_layout.addRow('Дата рождения:', self.birth_date_edit)
        form_layout.addRow('Специальность:', self.specialty_combo)
        form_layout.addRow('Преподаватель:', self.teacher_combo)
        form_layout.addRow('Телефон преподавателя:', self.teacher_phone_edit)
        form_layout.addRow('Руководитель практики:', self.practice_leader_combo)
        form_layout.addRow('Должность руководителя:', self.practice_leader_position_edit)
        form_layout.addRow('Организация руководителя:', self.practice_leader_org_edit)
        form_layout.addRow('Организация практики:', self.organization_combo)
        form_layout.addRow('Адрес организации:', self.organization_address_edit)
        form_layout.addRow('Модуль:', self.module_combo)
        form_layout.addRow('Тип практики:', self.practice_type_combo)
        form_layout.addRow(prod_dates_group)
        form_layout.addRow('Часы производственной практики:', self.practice_hours_edit)
        form_layout.addRow(study_dates_group)
        form_layout.addRow('Часы учебной практики:', self.study_practice_hours_edit)

        # Кнопка для управления справочниками
        btn_manage_refs = QPushButton('📚 Управление справочниками')
        btn_manage_refs.clicked.connect(self.open_reference_manager)
        btn_manage_refs.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                font-size: 12pt;
                font-weight: bold;
                background-color: #FF9800;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        form_layout.addRow('', btn_manage_refs)

        # Если редактирование, заполняем данные
        if self.student_data:
            self.load_student_data()

        scroll.setWidget(form_widget)
        layout.addWidget(scroll)

        # Кнопки ОК/Отмена увеличенные
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.setStyleSheet("""
            QPushButton {
                padding: 12px 30px;
                font-size: 12pt;
                min-width: 120px;
            }
        """)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

    def load_reference_data(self):
        """Загрузка данных в комбобоксы из БД"""
        if not self.db:
            return

        try:
            # Загружаем специальности
            specialties = self.db.get_specialties()
            self.specialty_combo.clear()
            self.specialty_combo.addItem('-- Выберите специальность --', None)
            for spec_id, code, name in specialties:
                display_text = f"{code} - {name}"
                self.specialty_combo.addItem(display_text, spec_id)

            # Загружаем преподаватели
            teachers = self.db.get_teachers()
            self.teacher_combo.clear()
            self.teacher_combo.addItem('-- Выберите преподавателя --', None)
            for teacher_id, name, phone in teachers:
                self.teacher_combo.addItem(name, (teacher_id, phone))

            # НОВОЕ: Загружаем руководителей практики
            practice_leaders = self.db.get_practice_leaders()
            self.practice_leader_combo.clear()
            self.practice_leader_combo.addItem('-- Выберите руководителя практики --', None)
            for leader_id, name, position, org_name, phone in practice_leaders:
                display_text = f"{name} ({position}, {org_name})"
                self.practice_leader_combo.addItem(display_text, (leader_id, position, org_name, phone))

            # Загружаем организации
            organizations = self.db.get_organizations()
            self.organization_combo.clear()
            self.organization_combo.addItem('-- Выберите организацию --', None)
            for org_id, name, address in organizations:
                self.organization_combo.addItem(name, (org_id, address))

            # Загружаем модули
            modules = self.db.get_modules()
            self.module_combo.clear()
            self.module_combo.addItem('-- Выберите модуль --', None)
            for module_id, name, hours in modules:
                display_text = f"{name} ({hours} ч.)"
                self.module_combo.addItem(display_text, (module_id, hours))

        except Exception as e:
            print(f"Ошибка загрузки справочников: {e}")

    def on_teacher_changed(self, index):
        """Обработчик изменения выбора преподавателя"""
        if index > 0:
            teacher_data = self.teacher_combo.currentData()
            if teacher_data:
                _, phone = teacher_data
                self.teacher_phone_edit.setText(phone)
        else:
            self.teacher_phone_edit.clear()

    def on_practice_leader_changed(self, index):
        """Обработчик изменения выбора руководителя практики"""
        if index > 0:
            leader_data = self.practice_leader_combo.currentData()
            if leader_data:
                _, position, org_name, phone = leader_data
                self.practice_leader_position_edit.setText(position)
                self.practice_leader_org_edit.setText(org_name)
        else:
            self.practice_leader_position_edit.clear()
            self.practice_leader_org_edit.clear()

    def on_organization_changed(self, index):
        """Обработчик изменения выбора организации"""
        if index > 0:
            org_data = self.organization_combo.currentData()
            if org_data:
                _, address = org_data
                self.organization_address_edit.setText(address)
        else:
            self.organization_address_edit.clear()

    def on_module_changed(self, index):
        """Обработчик изменения выбора модуля"""
        if index > 0:
            module_data = self.module_combo.currentData()
            if module_data:
                _, hours = module_data
                # Автоматически устанавливаем часы в соответствующее поле
                if self.practice_type_combo.currentText() == 'Производственная':
                    self.practice_hours_edit.setValue(hours)
                else:
                    self.study_practice_hours_edit.setValue(hours // 2)  # Учебная практика обычно короче

    def on_practice_type_changed(self, index):
        """Обработчик изменения типа практики"""
        practice_type = self.practice_type_combo.currentText()
        # Можно добавить логику скрытия/показа полей в зависимости от типа практики

    def open_reference_manager(self):
        """Открытие окна управления справочниками"""
        dialog = ReferenceManager(self, self.db)
        dialog.exec()
        # После закрытия окна справочников обновляем данные
        self.load_reference_data()

    def load_student_data(self):
        """Загрузка данных студента для редактирования"""
        if not self.student_data:
            return

        self.fio_edit.setText(self.student_data.get('full_name', ''))

        # Дата рождения
        birth_date = self.student_data.get('birth_date')
        if birth_date:
            try:
                if isinstance(birth_date, str):
                    # Пробуем разные форматы
                    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
                        try:
                            date_obj = QDate.fromString(birth_date, fmt)
                            if date_obj.isValid():
                                self.birth_date_edit.setDate(date_obj)
                                break
                        except:
                            continue
            except Exception as e:
                print(f"Ошибка загрузки даты рождения: {e}")

        # Специальность
        specialty_id = self.student_data.get('specialty_id')
        if specialty_id:
            for i in range(self.specialty_combo.count()):
                if self.specialty_combo.itemData(i) == specialty_id:
                    self.specialty_combo.setCurrentIndex(i)
                    break

        # Преподаватель
        teacher_id = self.student_data.get('teacher_id')
        teacher_phone = self.student_data.get('teacher_phone', '')
        if teacher_id:
            for i in range(self.teacher_combo.count()):
                data = self.teacher_combo.itemData(i)
                if data and data[0] == teacher_id:
                    self.teacher_combo.setCurrentIndex(i)
                    self.teacher_phone_edit.setText(teacher_phone)
                    break

        # Руководитель практики
        practice_leader_id = self.student_data.get('practice_leader_id')
        if practice_leader_id:
            for i in range(self.practice_leader_combo.count()):
                data = self.practice_leader_combo.itemData(i)
                if data and data[0] == practice_leader_id:
                    self.practice_leader_combo.setCurrentIndex(i)
                    self.practice_leader_position_edit.setText(self.student_data.get('practice_leader_position', ''))
                    self.practice_leader_org_edit.setText(self.student_data.get('practice_leader_org', ''))
                    break

        # Организация
        org_id = self.student_data.get('organization_id')
        org_address = self.student_data.get('organization_address', '')
        if org_id:
            for i in range(self.organization_combo.count()):
                data = self.organization_combo.itemData(i)
                if data and data[0] == org_id:
                    self.organization_combo.setCurrentIndex(i)
                    self.organization_address_edit.setText(org_address)
                    break

        # Модуль
        module_id = self.student_data.get('module_id')
        if module_id:
            for i in range(self.module_combo.count()):
                data = self.module_combo.itemData(i)
                if data and data[0] == module_id:
                    self.module_combo.setCurrentIndex(i)
                    break

        # Тип практики
        practice_type = self.student_data.get('practice_type', 'Производственная')
        if practice_type in ['Производственная', 'Учебная']:
            index = self.practice_type_combo.findText(practice_type)
            if index >= 0:
                self.practice_type_combo.setCurrentIndex(index)

        # Даты производственной практики
        practice_start_day = self.student_data.get('practice_start_day')
        if practice_start_day is not None:
            self.practice_start_day_edit.setValue(practice_start_day)

        month = self.student_data.get('practice_start_month', 'декабря')
        if month in ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                     'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']:
            self.practice_start_month_combo.setCurrentText(month)

        practice_start_year = self.student_data.get('practice_start_year')
        if practice_start_year is not None:
            self.practice_start_year_edit.setValue(practice_start_year)

        practice_end_day = self.student_data.get('practice_end_day')
        if practice_end_day is not None:
            self.practice_end_day_edit.setValue(practice_end_day)

        month = self.student_data.get('practice_end_month', 'декабря')
        if month in ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                     'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']:
            self.practice_end_month_combo.setCurrentText(month)

        practice_end_year = self.student_data.get('practice_end_year')
        if practice_end_year is not None:
            self.practice_end_year_edit.setValue(practice_end_year)

        practice_hours = self.student_data.get('practice_hours')
        if practice_hours is not None:
            self.practice_hours_edit.setValue(practice_hours)

        # Даты учебной практики
        study_practice_start_day = self.student_data.get('study_practice_start_day')
        if study_practice_start_day is not None:
            self.study_practice_start_day_edit.setValue(study_practice_start_day)

        month = self.student_data.get('study_practice_start_month', 'сентября')
        if month in ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                     'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']:
            self.study_practice_start_month_combo.setCurrentText(month)

        study_practice_start_year = self.student_data.get('study_practice_start_year')
        if study_practice_start_year is not None:
            self.study_practice_start_year_edit.setValue(study_practice_start_year)

        study_practice_end_day = self.student_data.get('study_practice_end_day')
        if study_practice_end_day is not None:
            self.study_practice_end_day_edit.setValue(study_practice_end_day)

        month = self.student_data.get('study_practice_end_month', 'октября')
        if month in ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                     'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']:
            self.study_practice_end_month_combo.setCurrentText(month)

        study_practice_end_year = self.student_data.get('study_practice_end_year')
        if study_practice_end_year is not None:
            self.study_practice_end_year_edit.setValue(study_practice_end_year)

        study_practice_hours = self.student_data.get('study_practice_hours')
        if study_practice_hours is not None:
            self.study_practice_hours_edit.setValue(study_practice_hours)

    def validate_and_accept(self):
        """Проверка данных перед принятием"""
        if not self.fio_edit.text().strip():
            QMessageBox.warning(self, 'Ошибка', 'Введите ФИО студента!')
            return

        if self.specialty_combo.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите специальность!')
            return

        if self.teacher_combo.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите преподавателя!')
            return

        if self.practice_leader_combo.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите руководителя практики!')
            return

        if self.organization_combo.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите организацию!')
            return

        if self.module_combo.currentIndex() == 0:
            QMessageBox.warning(self, 'Ошибка', 'Выберите модуль!')
            return

        self.accept()

    def get_data(self):
        """Получение данных из формы"""
        data = {
            'full_name': self.fio_edit.text().strip(),
            'birth_date': self.birth_date_edit.date().toString('yyyy-MM-dd'),
            'specialty_id': self.specialty_combo.currentData(),
            'module_id': self.module_combo.currentData()[0] if self.module_combo.currentData() else None,
            'teacher_id': self.teacher_combo.currentData()[0] if self.teacher_combo.currentData() else None,
            'practice_leader_id': self.practice_leader_combo.currentData()[0] if self.practice_leader_combo.currentData() else None,
            'organization_id': self.organization_combo.currentData()[0] if self.organization_combo.currentData() else None,
            'practice_type': self.practice_type_combo.currentText(),

            # Производственная практика
            'practice_start_day': self.practice_start_day_edit.value(),
            'practice_start_month': self.practice_start_month_combo.currentText(),
            'practice_start_year': self.practice_start_year_edit.value(),
            'practice_end_day': self.practice_end_day_edit.value(),
            'practice_end_month': self.practice_end_month_combo.currentText(),
            'practice_end_year': self.practice_end_year_edit.value(),
            'practice_hours': self.practice_hours_edit.value(),

            # Учебная практика
            'study_practice_start_day': self.study_practice_start_day_edit.value(),
            'study_practice_start_month': self.study_practice_start_month_combo.currentText(),
            'study_practice_start_year': self.study_practice_start_year_edit.value(),
            'study_practice_end_day': self.study_practice_end_day_edit.value(),
            'study_practice_end_month': self.study_practice_end_month_combo.currentText(),
            'study_practice_end_year': self.study_practice_end_year_edit.value(),
            'study_practice_hours': self.study_practice_hours_edit.value()
        }

        return data


class PracticeManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = None
        self.doc_gen = UniversalDocumentGenerator()  # ИСПОЛЬЗУЕМ УНИВЕРСАЛЬНЫЙ ГЕНЕРАТОР
        self.init_ui()

        # Показываем окно подключения к БД
        self.show_db_config_window()

    def init_ui(self):
        self.setWindowTitle('Менеджер производственной практики - ГБПОУ МО "Люберецкий техникум"')
        self.setGeometry(100, 100, 1400, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)

        # Верхняя панель с информацией о подключении
        self.connection_panel = QHBoxLayout()
        self.connection_label = QLabel("Не подключено к базе данных")
        self.connection_label.setStyleSheet("""
            color: #f44336;
            font-weight: bold;
            padding: 8px;
            background-color: #2d2d2d;
            border-radius: 4px;
        """)

        self.reconnect_button = QPushButton("⚙️ Изменить подключение")
        self.reconnect_button.clicked.connect(self.show_db_config_window)
        self.reconnect_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #FF9800;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)

        self.connection_panel.addWidget(self.connection_label)
        self.connection_panel.addStretch()
        self.connection_panel.addWidget(self.reconnect_button)

        main_layout.addLayout(self.connection_panel)

        # Панель управления
        control_panel = QHBoxLayout()
        control_panel.setSpacing(10)

        # Кнопки управления
        self.btn_backup = QPushButton('💾 Бэкап БД')
        self.btn_backup.clicked.connect(self.manage_backups)
        self.btn_backup.setToolTip('Управление резервных копий базы данных')

        self.btn_add_group = QPushButton('➕ Добавить группу')
        self.btn_add_group.clicked.connect(self.add_group)
        self.btn_add_group.setToolTip('Добавить новую группу студентов')

        self.btn_edit_group = QPushButton('✏️ Редактировать группу')
        self.btn_edit_group.clicked.connect(self.edit_group)
        self.btn_edit_group.setToolTip('Изменить название группы')

        self.btn_delete_group = QPushButton('🗑️ Удалить группу')
        self.btn_delete_group.clicked.connect(self.delete_group)
        self.btn_delete_group.setToolTip('Удалить группу и всех её студентов')

        # Кнопка управления справочниками
        self.btn_manage_refs = QPushButton('📚 Управление справочниками')
        self.btn_manage_refs.clicked.connect(self.manage_references)
        self.btn_manage_refs.setToolTip('Управление специальностями, преподавателями, организациями и модулями')

        # Добавляем кнопки в панель управления
        control_panel.addWidget(self.btn_backup)
        control_panel.addWidget(self.btn_add_group)
        control_panel.addWidget(self.btn_edit_group)
        control_panel.addWidget(self.btn_delete_group)
        control_panel.addStretch()
        control_panel.addWidget(self.btn_manage_refs)

        main_layout.addLayout(control_panel)

        # Панель работы с шаблонами
        templates_panel = QHBoxLayout()
        templates_panel.setSpacing(10)

        # Кнопка обновления списка шаблонов
        self.btn_refresh_templates = QPushButton('🔄 Обновить шаблоны')
        self.btn_refresh_templates.clicked.connect(self.refresh_templates_list)
        self.btn_refresh_templates.setToolTip('Обновить список доступных шаблонов')

        # Выпадающий список шаблонов
        templates_panel.addWidget(QLabel('Шаблон:'))
        self.templates_combo = QComboBox()
        self.templates_combo.setMinimumWidth(300)
        self.templates_combo.setToolTip('Выберите шаблон для генерации')
        self.templates_combo.currentTextChanged.connect(self.on_template_selected)
        templates_panel.addWidget(self.templates_combo)

        # Кнопка генерации выбранного шаблона
        self.btn_generate_selected = QPushButton('📄 Сгенерировать')
        self.btn_generate_selected.clicked.connect(self.generate_selected_template)
        self.btn_generate_selected.setToolTip('Сгенерировать выбранный шаблон')
        self.btn_generate_selected.setEnabled(False)
        templates_panel.addWidget(self.btn_generate_selected)

        # Кнопка генерации всех шаблонов
        self.btn_generate_all = QPushButton('📁 Все шаблоны')
        self.btn_generate_all.clicked.connect(self.generate_all_templates)
        self.btn_generate_all.setToolTip('Сгенерировать все доступные шаблоны')
        templates_panel.addWidget(self.btn_generate_all)

        # Кнопка просмотра переменных в конкретном шаблоне
        self.btn_view_variables = QPushButton('🔍 Переменные шаблона')
        self.btn_view_variables.clicked.connect(self.view_template_variables)
        self.btn_view_variables.setToolTip('Просмотреть переменные в выбранном шаблоне')
        self.btn_view_variables.setEnabled(False)
        templates_panel.addWidget(self.btn_view_variables)

        # НОВАЯ КНОПКА: Просмотр всех доступных переменных
        self.btn_view_all_variables = QPushButton('📋 Все переменные')
        self.btn_view_all_variables.clicked.connect(self.view_all_variables)
        self.btn_view_all_variables.setToolTip('Просмотреть все доступные переменные для создания новых шаблонов')
        templates_panel.addWidget(self.btn_view_all_variables)

        templates_panel.addStretch()
        main_layout.addLayout(templates_panel)

        # Основная область с разделением
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - список студентов
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)

        # Выбор группы
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel('Группа:'))
        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self.on_group_changed)
        self.group_combo.setMinimumWidth(200)
        group_layout.addWidget(self.group_combo)

        self.student_count_label = QLabel('Студентов: 0')
        self.student_count_label.setStyleSheet('color: #888; font-style: italic;')
        group_layout.addStretch()
        group_layout.addWidget(self.student_count_label)

        left_layout.addLayout(group_layout)

        # Таблица студентов
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(4)
        self.student_table.setHorizontalHeaderLabels(['ID', 'ФИО', 'Дата рождения', 'Группа'])
        self.student_table.setAlternatingRowColors(True)
        self.student_table.verticalHeader().setVisible(False)
        self.student_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.student_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.student_table.itemSelectionChanged.connect(self.on_student_selected)

        # Установка ширины колонок
        self.student_table.setColumnWidth(0, 50)   # ID
        self.student_table.setColumnWidth(1, 300)  # ФИО
        self.student_table.setColumnWidth(2, 120)  # Дата рождения
        self.student_table.setColumnWidth(3, 150)  # Группа

        left_layout.addWidget(self.student_table)

        # Кнопки управления студентами
        student_buttons = QHBoxLayout()
        student_buttons.setSpacing(10)

        self.btn_add_student = QPushButton('➕ Добавить студента')
        self.btn_add_student.clicked.connect(self.add_student)

        self.btn_edit_student = QPushButton('✏️ Редактировать')
        self.btn_edit_student.clicked.connect(self.edit_student)

        self.btn_delete_student = QPushButton('🗑️ Удалить студента')
        self.btn_delete_student.clicked.connect(self.delete_student)

        self.btn_refresh = QPushButton('🔄 Обновить')
        self.btn_refresh.clicked.connect(self.refresh_data)

        student_buttons.addWidget(self.btn_add_student)
        student_buttons.addWidget(self.btn_edit_student)
        student_buttons.addWidget(self.btn_delete_student)
        student_buttons.addStretch()
        student_buttons.addWidget(self.btn_refresh)

        left_layout.addLayout(student_buttons)

        # Правая панель - детальная информация о студенте
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)

        # Заголовок формы
        self.form_header = QLabel('Выберите студента')
        self.form_header.setStyleSheet('font-size: 12pt; font-weight: bold; color: #2196F3; margin-bottom: 10px;')
        self.form_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.form_header)

        # Прокручиваемая область для формы
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.form_layout.setSpacing(8)

        # Поля формы
        self.fio_label = QLabel('')
        self.birth_date_label = QLabel('')
        self.specialty_label = QLabel('')
        self.teacher_label = QLabel('')
        self.teacher_phone_label = QLabel('')
        self.organization_label = QLabel('')
        self.organization_address_label = QLabel('')
        self.module_label = QLabel('')
        self.practice_dates_label = QLabel('')
        self.practice_hours_label = QLabel('')

        # НОВЫЕ ПОЛЯ
        self.practice_leader_label = QLabel('')
        self.practice_type_label = QLabel('')
        self.study_practice_dates_label = QLabel('')
        self.study_practice_hours_label = QLabel('')

        # Устанавливаем перенос текста
        for label in [self.organization_address_label, self.study_practice_dates_label]:
            label.setWordWrap(True)

        # Добавляем поля в форму
        self.form_layout.addRow('ФИО:', self.fio_label)
        self.form_layout.addRow('Дата рождения:', self.birth_date_label)
        self.form_layout.addRow('Специальность:', self.specialty_label)
        self.form_layout.addRow('Преподаватель:', self.teacher_label)
        self.form_layout.addRow('Телефон преподавателя:', self.teacher_phone_label)
        self.form_layout.addRow('Руководитель практики:', self.practice_leader_label)
        self.form_layout.addRow('Организация:', self.organization_label)
        self.form_layout.addRow('Адрес организации:', self.organization_address_label)
        self.form_layout.addRow('Модуль:', self.module_label)
        self.form_layout.addRow('Тип практики:', self.practice_type_label)
        self.form_layout.addRow('Даты производственной практики:', self.practice_dates_label)
        self.form_layout.addRow('Часы производственной практики:', self.practice_hours_label)
        self.form_layout.addRow('Даты учебной практики:', self.study_practice_dates_label)
        self.form_layout.addRow('Часы учебной практики:', self.study_practice_hours_label)

        scroll.setWidget(self.form_widget)
        right_layout.addWidget(scroll)

        # Лог действий
        log_header = QLabel('Лог действий:')
        log_header.setStyleSheet('font-weight: bold; color: #888;')
        right_layout.addWidget(log_header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Consolas', 'Monospace';
                font-size: 10pt;
            }
        """)
        right_layout.addWidget(self.log_text)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([800, 600])

        main_layout.addWidget(splitter)

        # Статус бар
        self.statusBar().showMessage('Готово')

        # Отключаем все элементы до подключения
        self.set_ui_enabled(False)

        # Применение темного стиля
        self.setStyleSheet(dark_style)

        # Загружаем список шаблонов
        self.refresh_templates_list()

    def manage_backups(self):
        """Управление бэкапами базы данных"""
        from backup_manager import BackupManager

        # Получаем конфигурацию из переменных окружения
        config = {
            'DB_HOST': os.environ.get('DB_HOST', 'localhost'),
            'DB_PORT': os.environ.get('DB_PORT', '5432'),
            'DB_NAME': os.environ.get('DB_NAME', 'practice_db'),
            'DB_USER': os.environ.get('DB_USER', 'postgres'),
            'DB_PASSWORD': os.environ.get('DB_PASSWORD', '')
        }

        dialog = BackupManager(self, config)  # Передаем self как parent
        dialog.exec()

    def show_db_config_window(self):
        """Показывает окно настройки подключения к БД"""
        dialog = DBConfigWindow(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = dialog.get_config()
            self.connect_to_database(config)
        else:
            # Если пользователь отменил, спрашиваем выйти
            if not self.db:
                reply = QMessageBox.question(
                    self, 'Подключение отменено',
                    'Не указаны данные для подключения. Выйти из программы?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.close()

    def connect_to_database(self, config):
        """Подключается к базе данных с указанными параметрами"""
        try:
            # Сохраняем конфигурацию в переменные окружения
            os.environ['DB_HOST'] = config.get('DB_HOST', 'localhost')
            os.environ['DB_PORT'] = config.get('DB_PORT', '5432')
            os.environ['DB_NAME'] = config.get('DB_NAME', 'practice_db')
            os.environ['DB_USER'] = config.get('DB_USER', 'postgres')
            os.environ['DB_PASSWORD'] = config.get('DB_PASSWORD', '')

            # Пробуем подключиться
            self.db = DatabaseManager()

            if self.db.connection:
                self.connection_label.setText(f"✓ Подключено к {config['DB_HOST']}:{config['DB_PORT']} ({config['DB_NAME']})")
                self.connection_label.setStyleSheet("""
                    color: #4CAF50;
                    font-weight: bold;
                    padding: 8px;
                    background-color: #2d2d2d;
                    border-radius: 4px;
                """)
                self.set_ui_enabled(True)
                self.load_groups()
                self.log_message("Подключение к базе данных установлено")

                # Проверяем, есть ли студенты
                student_count = self.db.get_student_count()
                if student_count == 0:
                    self.log_message("В базе данных нет студентов")
                else:
                    self.log_message(f"Найдено {student_count} студентов в базе данных")
            else:
                self.connection_label.setText("✗ Не удалось подключиться")
                self.connection_label.setStyleSheet("""
                    color: #f44336;
                    font-weight: bold;
                    padding: 8px;
                    background-color: #2d2d2d;
                    border-radius: 4px;
                """)
                self.set_ui_enabled(False)
                self.log_message("Ошибка подключения к базе данных")

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка подключения', f'Не удалось подключиться:\n{str(e)}')
            self.connection_label.setText("✗ Ошибка подключения")
            self.connection_label.setStyleSheet("""
                color: #f44336;
                font-weight: bold;
                padding: 8px;
                background-color: #2d2d2d;
                border-radius: 4px;
            """)
            self.set_ui_enabled(False)
            self.log_message(f"Ошибка подключения: {str(e)}")

    def set_ui_enabled(self, enabled):
        """Включает или отключает элементы интерфейса"""
        self.btn_backup.setEnabled(enabled)
        self.btn_add_group.setEnabled(enabled)
        self.btn_edit_group.setEnabled(enabled)
        self.btn_delete_group.setEnabled(enabled)
        self.btn_manage_refs.setEnabled(enabled)
        self.btn_refresh_templates.setEnabled(enabled)
        self.templates_combo.setEnabled(enabled)
        self.btn_generate_selected.setEnabled(enabled and self.templates_combo.currentText() != "Нет шаблонов в папке templates/")
        self.btn_generate_all.setEnabled(enabled and self.templates_combo.count() > 0)
        self.btn_view_variables.setEnabled(enabled and self.templates_combo.currentText() != "Нет шаблонов в папке templates/")
        self.btn_view_all_variables.setEnabled(enabled)
        self.group_combo.setEnabled(enabled)
        self.btn_add_student.setEnabled(enabled)
        self.btn_edit_student.setEnabled(enabled)
        self.btn_delete_student.setEnabled(enabled)
        self.btn_refresh.setEnabled(enabled)

        # Очищаем таблицу если отключено
        if not enabled:
            self.student_table.setRowCount(0)
            self.group_combo.clear()
            self.clear_form()

    def refresh_database_connection(self):
        try:
            # Закрываем старое подключение
            if self.db and self.db.connection:
                self.db.connection.close()

            # Создаем новое подключение
            self.db = DatabaseManager()

            if self.db.connection:
                # Обновляем данные в интерфейсе
                self.load_groups()
                self.log_message("✅ Подключение к базе данных обновлено после восстановления")

                # Обновляем информацию о подключении
                config = {
                    'DB_HOST': os.environ.get('DB_HOST', 'localhost'),
                    'DB_PORT': os.environ.get('DB_PORT', '5432'),
                    'DB_NAME': os.environ.get('DB_NAME', 'practice_db'),
                    'DB_USER': os.environ.get('DB_USER', 'postgres')
                }

                self.connection_label.setText(f"✓ Подключено к {config['DB_HOST']}:{config['DB_PORT']} ({config['DB_NAME']})")
                self.connection_label.setStyleSheet("""
                    color: #4CAF50;
                    font-weight: bold;
                    padding: 8px;
                    background-color: #2d2d2d;
                    border-radius: 4px;
                """)

                return True
            else:
                self.log_message("❌ Не удалось обновить подключение к базе данных")
                return False

        except Exception as e:
            self.log_message(f"❌ Ошибка обновления подключения: {str(e)}")
            return False

    def clear_form(self):
        """Очищает форму просмотра"""
        self.form_header.setText('Выберите студента')
        self.fio_label.setText('')
        self.birth_date_label.setText('')
        self.specialty_label.setText('')
        self.teacher_label.setText('')
        self.teacher_phone_label.setText('')
        self.practice_leader_label.setText('')
        self.organization_label.setText('')
        self.organization_address_label.setText('')
        self.module_label.setText('')
        self.practice_type_label.setText('')
        self.practice_dates_label.setText('')
        self.practice_hours_label.setText('')
        self.study_practice_dates_label.setText('')
        self.study_practice_hours_label.setText('')

    def load_groups(self):
        """Загрузка списка групп"""
        try:
            groups_data = self.db.get_groups()
            self.group_combo.clear()
            self.group_combo.addItem('-- Все группы --', None)

            # Исправление: получаем все значения из кортежа, но используем только первые два
            for group_row in groups_data:
                # Берем первые два значения (ID и название)
                if len(group_row) >= 2:
                    group_id = group_row[0]
                    group_name = group_row[1]
                    self.group_combo.addItem(group_name, group_id)
                else:
                    # Если что-то пошло не так, пропускаем эту запись
                    print(f"Неверный формат данных группы: {group_row}")
        except Exception as e:
            self.log_message(f"Ошибка загрузки групп: {str(e)}")
            print(f"Ошибка загрузки групп (подробно): {e}")

    def on_group_changed(self):
        """Обработчик изменения выбора группы"""
        group_id = self.group_combo.currentData()
        if group_id is None:
            self.load_all_students()
        else:
            self.load_students_by_group(group_id)

    def load_all_students(self):
        """Загрузка всех студентов"""
        try:
            # Получаем все группы
            groups_data = self.db.get_groups()
            all_students = []

            for group_row in groups_data:
                if len(group_row) >= 2:
                    group_id = group_row[0]
                    group_name = group_row[1]
                    students = self.db.get_students_by_group(group_id)
                    for student in students:
                        if len(student) >= 3:
                            student_id, full_name, birth_date = student[0], student[1], student[2]
                            all_students.append((student_id, full_name, birth_date, group_name))

            self.display_students(all_students)

        except Exception as e:
            self.log_message(f"Ошибка загрузки всех студентов: {str(e)}")

    def load_students_by_group(self, group_id):
        """Загрузка студентов по группе"""
        try:
            students = self.db.get_students_by_group(group_id)
            group_name = self.group_combo.currentText()

            # Преобразуем данные для отображения
            display_data = []
            for student in students:
                if len(student) >= 3:
                    student_id, full_name, birth_date = student[0], student[1], student[2]
                    display_data.append((student_id, full_name, birth_date, group_name))

            self.display_students(display_data)

        except Exception as e:
            self.log_message(f"Ошибка загрузки студентов: {str(e)}")

    def display_students(self, students):
        """Отображение студентов в таблице"""
        self.student_table.setRowCount(0)

        for row, (student_id, full_name, birth_date, group_name) in enumerate(students):
            self.student_table.insertRow(row)
            self.student_table.setItem(row, 0, QTableWidgetItem(str(student_id)))
            self.student_table.setItem(row, 1, QTableWidgetItem(full_name))
            self.student_table.setItem(row, 2, QTableWidgetItem(birth_date))
            self.student_table.setItem(row, 3, QTableWidgetItem(group_name))

        # Обновляем счетчик
        self.student_count_label.setText(f"Студентов: {len(students)}")

        if students:
            self.log_message(f"Загружено {len(students)} студентов")
        else:
            self.log_message("В выбранной группе нет студентов")

    def on_student_selected(self):
        """Обработчик выбора студента в таблице"""
        current_row = self.student_table.currentRow()
        if current_row >= 0:
            student_id = self.student_table.item(current_row, 0).text()
            student_name = self.student_table.item(current_row, 1).text()

            try:
                student_data = self.db.get_student_details(student_id)
                if student_data:
                    self.display_student_details(student_data)
                    self.form_header.setText(f"Студент: {student_name}")
                else:
                    self.clear_form()
                    self.form_header.setText(f"Студент: {student_name} (нет данных о практике)")
            except Exception as e:
                self.log_message(f"Ошибка загрузки данных студента: {str(e)}")
        else:
            self.clear_form()

    def display_student_details(self, student_data):
        """Отображение детальной информации о студенте"""
        self.fio_label.setText(student_data.get('full_name', ''))

        # Дата рождения
        birth_date = student_data.get('birth_date', '')
        self.birth_date_label.setText(str(birth_date) if birth_date else 'Не указана')

        # НОВОЕ: Форма обучения
        study_form = student_data.get('study_form', '')
        specialty_name = student_data.get('specialty_name', 'Не указана')
        if study_form:
            self.specialty_label.setText(f"{specialty_name} ({study_form})")
        else:
            self.specialty_label.setText(specialty_name)

        self.teacher_label.setText(student_data.get('teacher_name', 'Не указан'))
        self.teacher_phone_label.setText(student_data.get('teacher_phone', 'Не указан'))

        # НОВОЕ: Руководитель практики
        practice_leader_name = student_data.get('practice_leader_name', 'Не указан')
        practice_leader_position = student_data.get('practice_leader_position', '')
        practice_leader_org = student_data.get('practice_leader_org', '')

        if practice_leader_name != 'Не указан':
            leader_text = practice_leader_name
            if practice_leader_position or practice_leader_org:
                leader_text += f" ({practice_leader_position}"
                if practice_leader_org:
                    leader_text += f", {practice_leader_org}"
                leader_text += ")"
            self.practice_leader_label.setText(leader_text)
        else:
            self.practice_leader_label.setText(practice_leader_name)

        self.organization_label.setText(student_data.get('organization_name', 'Не указана'))
        self.organization_address_label.setText(student_data.get('organization_address', 'Не указан'))

        self.module_label.setText(student_data.get('module_name', 'Не указан'))

        # НОВОЕ: Тип практики
        practice_type = student_data.get('practice_type', 'Производственная')
        self.practice_type_label.setText(practice_type)

        # Форматируем даты производственной практики
        start_day = student_data.get('practice_start_day', '')
        start_month = student_data.get('practice_start_month', '')
        start_year = student_data.get('practice_start_year', '')
        end_day = student_data.get('practice_end_day', '')
        end_month = student_data.get('practice_end_month', '')
        end_year = student_data.get('practice_end_year', '')

        if start_day and start_month and start_year:
            prod_start_date = f"{start_day} {start_month} {start_year}"
        else:
            prod_start_date = "Не указано"

        if end_day and end_month and end_year:
            prod_end_date = f"{end_day} {end_month} {end_year}"
        else:
            prod_end_date = "Не указано"

        self.practice_dates_label.setText(f"с {prod_start_date} по {prod_end_date}")

        # НОВОЕ: Форматируем даты учебной практики
        study_start_day = student_data.get('study_practice_start_day', '')
        study_start_month = student_data.get('study_practice_start_month', '')
        study_start_year = student_data.get('study_practice_start_year', '')
        study_end_day = student_data.get('study_practice_end_day', '')
        study_end_month = student_data.get('study_practice_end_month', '')
        study_end_year = student_data.get('study_practice_end_year', '')

        if study_start_day and study_start_month and study_start_year:
            study_start_date = f"{study_start_day} {study_start_month} {study_start_year}"
        else:
            study_start_date = "Не указано"

        if study_end_day and study_end_month and study_end_year:
            study_end_date = f"{study_end_day} {study_end_month} {study_end_year}"
        else:
            study_end_date = "Не указано"

        self.study_practice_dates_label.setText(f"с {study_start_date} по {study_end_date}")

        # Часы практики
        practice_hours = student_data.get('practice_hours', 0)
        study_practice_hours = student_data.get('study_practice_hours', 0)
        self.practice_hours_label.setText(str(practice_hours))
        self.study_practice_hours_label.setText(str(study_practice_hours))

    def manage_references(self):
        """Управление справочниками"""
        dialog = ReferenceManager(self, self.db)
        dialog.exec()

    def add_group(self):
        """Добавление новой группы"""
        name, ok = QInputDialog.getText(self, 'Новая группа', 'Введите название группы:')
        if ok and name:
            if not name.strip():
                QMessageBox.warning(self, 'Ошибка', 'Название группы не может быть пустым!')
                return

            try:
                group_id = self.db.add_group(name)
                if group_id:
                    self.load_groups()
                    self.log_message(f"Добавлена группа: {name}")
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось добавить группу (возможно, такая группа уже существует)')
            except Exception as e:
                self.log_message(f"Ошибка добавления группы: {str(e)}")
                QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить группу:\n{str(e)}')

    def edit_group(self):
        """Редактирование группы"""
        current_index = self.group_combo.currentIndex()
        if current_index <= 0:  # 0 - это "Все группы"
            QMessageBox.warning(self, 'Внимание', 'Выберите группу для редактирования!')
            return

        group_id = self.group_combo.currentData()
        current_name = self.group_combo.currentText()

        new_name, ok = QInputDialog.getText(self, 'Редактирование группы',
                                           'Введите новое название группы:',
                                           text=current_name)
        if ok and new_name and new_name != current_name:
            if not new_name.strip():
                QMessageBox.warning(self, 'Ошибка', 'Название группы не может быть пустым!')
                return

            try:
                if self.db.update_group(group_id, new_name):
                    self.load_groups()
                    self.log_message(f"Группа переименована: {current_name} → {new_name}")
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось переименовать группу')
            except Exception as e:
                self.log_message(f"Ошибка редактирования группы: {str(e)}")
                QMessageBox.critical(self, 'Ошибка', f'Не удалось переименовать группу:\n{str(e)}')

    def delete_group(self):
        """Удаление группы"""
        current_index = self.group_combo.currentIndex()
        if current_index <= 0:  # 0 - это "Все группы"
            QMessageBox.warning(self, 'Внимание', 'Выберите группу для удаления!')
            return

        group_id = self.group_combo.currentData()
        group_name = self.group_combo.currentText()

        reply = QMessageBox.question(
            self, 'Удаление группы',
            f'Вы уверены, что хотите удалить группу "{group_name}" и всех её студентов?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db.delete_group(group_id):
                    self.load_groups()
                    self.log_message(f"Удалена группа: {group_name}")
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось удалить группу')
            except Exception as e:
                self.log_message(f"Ошибка удаления группы: {str(e)}")
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить группу:\n{str(e)}')

    def add_student(self):
        """Добавление нового студента"""
        # Получаем выбранную группу
        current_index = self.group_combo.currentIndex()
        if current_index <= 0:  # 0 - это "Все группы"
            QMessageBox.warning(self, 'Внимание', 'Сначала выберите группу для добавления студента!')
            return

        group_id = self.group_combo.currentData()
        group_name = self.group_combo.currentText()

        dialog = StudentDialog(self, None, self.db)
        if dialog.exec():
            student_data = dialog.get_data()
            student_data['group_id'] = group_id

            try:
                student_id = self.db.add_student(student_data)
                if student_id:
                    self.on_group_changed()  # Обновляем список студентов
                    self.log_message(f"Добавлен студент: {student_data['full_name']} в группу {group_name}")
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось добавить студента')
            except Exception as e:
                self.log_message(f"Ошибка добавления студента: {str(e)}")
                QMessageBox.critical(self, 'Ошибка', f'Не удалось добавить студента:\n{str(e)}')

    def edit_student(self):
        """Редактирование выбранного студента"""
        current_row = self.student_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите студента для редактирования!')
            return

        student_id = self.student_table.item(current_row, 0).text()

        try:
            student_data = self.db.get_student_details(student_id)
            if not student_data:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить данные студента')
                return

            # Проверяем и заменяем None значения на значения по умолчанию
            student_data = self._sanitize_student_data(student_data)

            dialog = StudentDialog(self, student_data, self.db)
            if dialog.exec():
                updated_data = dialog.get_data()
                updated_data['group_id'] = student_data.get('group_id')

                if self.db.update_student(student_id, updated_data):
                    self.on_group_changed()  # Обновляем список студентов
                    self.log_message(f"Обновлен студент: {updated_data['full_name']}")
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось обновить данные студента')

        except Exception as e:
            self.log_message(f"Ошибка редактирования студента: {str(e)}")
            QMessageBox.critical(self, 'Ошибка', f'Не удалось отредактировать студента:\n{str(e)}"')

    def _sanitize_student_data(self, student_data):
        """Очистка данных студента от None значений"""
        sanitized = student_data.copy()

        # Заменяем None значения на значения по умолчанию
        defaults = {
            'practice_start_day': 8,
            'practice_end_day': 21,
            'practice_start_year': 2025,
            'practice_end_year': 2025,
            'practice_hours': 72,
            'study_practice_start_day': 1,
            'study_practice_end_day': 30,
            'study_practice_start_year': 2025,
            'study_practice_end_year': 2025,
            'study_practice_hours': 36
        }

        for key, default_value in defaults.items():
            if sanitized.get(key) is None:
                sanitized[key] = default_value

        return sanitized

    def delete_student(self):
        """Удаление выбранного студента"""
        current_row = self.student_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите студента для удаления!')
            return

        student_id = self.student_table.item(current_row, 0).text()
        student_name = self.student_table.item(current_row, 1).text()

        reply = QMessageBox.question(
            self, 'Удаление студента',
            f'Вы уверены, что хотите удалить студента "{student_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.db.delete_student(student_id):
                    self.on_group_changed()  # Обновляем список студентов
                    self.log_message(f"Удален студент: {student_name}")
                else:
                    QMessageBox.warning(self, 'Ошибка', 'Не удалось удалить студента')
            except Exception as e:
                self.log_message(f"Ошибка удаления студента: {str(e)}")
                QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить студента:\n{str(e)}')

    def refresh_data(self):
        """Обновление данных"""
        self.load_groups()
        self.log_message("Данные обновлены")

    def refresh_templates_list(self):
        """Обновление списка доступных шаблонов"""
        templates = self.doc_gen.get_available_templates()
        self.templates_combo.clear()

        if templates:
            self.templates_combo.addItems(templates)
            self.btn_generate_all.setEnabled(True)
            self.log_message(f"Загружено {len(templates)} шаблонов")
        else:
            self.templates_combo.addItem("Нет шаблонов в папке templates/")
            self.btn_generate_all.setEnabled(False)
            self.btn_generate_selected.setEnabled(False)
            self.btn_view_variables.setEnabled(False)
            self.log_message("В папке templates нет шаблонов .docx")

    def on_template_selected(self):
        """Обработчик выбора шаблона в комбобоксе"""
        has_selection = (self.templates_combo.currentText() != "Нет шаблонов в папке templates/"
                        and self.templates_combo.currentText() != "")
        self.btn_generate_selected.setEnabled(has_selection)
        self.btn_view_variables.setEnabled(has_selection)

    def generate_selected_template(self):
        """Генерация выбранного шаблона"""
        current_row = self.student_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите студента!')
            return

        template_name = self.templates_combo.currentText()
        if not template_name or template_name == "Нет шаблонов в папке templates/":
            return

        student_id = self.student_table.item(current_row, 0).text()
        student_name = self.student_table.item(current_row, 1).text()

        try:
            student_data = self.db.get_student_details(student_id)
            if not student_data:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить данные студента')
                return

            self.log_message(f"Генерация '{template_name}' для: {student_name}")

            # Генерация документа
            output_path = self.doc_gen.generate_document(template_name, student_data)

            # Показать сообщение об успехе
            self.show_success_message(
                f"Документ сгенерирован для {student_name}",
                f"Шаблон: {template_name}\n\nФайл сохранен в:\n{output_path}",
                output_path
            )

        except Exception as e:
            self.log_message(f"Ошибка генерации документа: {str(e)}")
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сгенерировать документ:\n{str(e)}')

    def generate_all_templates(self):
        """Генерация всех доступных шаблонов"""
        current_row = self.student_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, 'Внимание', 'Выберите студента!')
            return

        student_id = self.student_table.item(current_row, 0).text()
        student_name = self.student_table.item(current_row, 1).text()

        # Подтверждение
        reply = QMessageBox.question(
            self, 'Подтверждение',
            f'Сгенерировать все шаблоны для студента "{student_name}"?\n\n'
            f'Будут созданы документы для всех шаблонов в папке templates/.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            student_data = self.db.get_student_details(student_id)
            if not student_data:
                QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить данные студента')
                return

            self.log_message(f"Генерация всех шаблонов для: {student_name}")

            # Генерация всех документов
            results = self.doc_gen.generate_all_documents(student_data)

            # Подсчет результатов
            success_count = sum(1 for r in results if r[2] == 'success')
            error_count = sum(1 for r in results if r[2] == 'error')

            # Формирование детального отчета
            report = f"Сгенерировано документов: {success_count} из {len(results)}\n"

            if error_count > 0:
                report += f"\nОшибки ({error_count}):\n"
                for template, error_msg, status in results:
                    if status == 'error':
                        report += f"• {template}: {error_msg[:100]}...\n"

            # Список успешных файлов
            if success_count > 0:
                report += f"\nУспешно сгенерированы:\n"
                for template, output_path, status in results:
                    if status == 'success':
                        filename = os.path.basename(output_path)
                        report += f"• {filename}\n"

            # Показать отчет
            self.show_success_message(
                f"Генерация завершена",
                report,
                self.doc_gen.output_dir
            )

            self.log_message(f"✓ Сгенерировано {success_count} документов для {student_name}")

        except Exception as e:
            self.log_message(f"Ошибка генерации документов: {str(e)}")
            QMessageBox.critical(self, 'Ошибка', f'Не удалось сгенерировать документы:\n{str(e)}')

    def view_template_variables(self):
        """Просмотр переменных в выбранном шаблоне"""
        template_name = self.templates_combo.currentText()
        if not template_name or template_name == "Нет шаблонов в папке templates/":
            return

        variables = self.doc_gen.get_template_variables(template_name)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Переменные в шаблоне: {template_name}")
        dialog.setFixedSize(500, 400)

        layout = QVBoxLayout(dialog)

        # Заголовок
        title = QLabel(f"Найдено {len(variables)} переменных:")
        title.setStyleSheet('font-size: 12pt; font-weight: bold; color: #2196F3;')
        layout.addWidget(title)

        # Список переменных
        if variables:
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText('\n'.join(sorted(variables)))
            text_edit.setStyleSheet("""
                QTextEdit {
                    font-family: 'Courier New', monospace;
                    font-size: 11pt;
                    background-color: #2d2d2d;
                    border: 1px solid #555;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
            layout.addWidget(text_edit)
        else:
            label = QLabel("В шаблоне не найдено переменных в формате {{variable}}")
            label.setStyleSheet('color: #888; font-style: italic; padding: 20px;')
            layout.addWidget(label)

        # Кнопка закрытия
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec()

    def view_all_variables(self):
        """Просмотр всех доступных переменных для создания шаблонов"""
        dialog = QDialog(self)
        dialog.setWindowTitle("📋 Все доступные переменные для шаблонов")
        dialog.setFixedSize(800, 600)

        layout = QVBoxLayout(dialog)

        # Заголовок
        title = QLabel("Переменные для использования в шаблонах")
        title.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #4CAF50;
            margin-bottom: 15px;
            padding: 10px;
            border-bottom: 2px solid #4CAF50;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Вкладки для разных категорий переменных
        tab_widget = QTabWidget()

        # Получаем переменные по категориям
        variables_by_category = self.doc_gen.get_all_available_variables()

        for category_name, variables_dict in variables_by_category.items():
            category_widget = QWidget()
            category_layout = QVBoxLayout(category_widget)
            category_layout.setSpacing(5)

            # Название категории
            category_label = QLabel(self._get_category_title(category_name))
            category_label.setStyleSheet("""
                font-size: 12pt;
                font-weight: bold;
                color: #2196F3;
                margin-bottom: 10px;
            """)
            category_layout.addWidget(category_label)

            # Таблица переменных
            table = QTableWidget()
            table.setColumnCount(2)
            table.setHorizontalHeaderLabels(["Переменная", "Описание"])
            table.setRowCount(len(variables_dict))

            # Заполняем таблицу
            for i, (var_name, description) in enumerate(variables_dict.items()):
                # Имя переменной в формате для шаблона
                variable_cell = QTableWidgetItem(f"{{{{{var_name}}}}}")
                variable_cell.setFont(QFont("Courier New", 10))
                variable_cell.setFlags(variable_cell.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

                description_cell = QTableWidgetItem(description)
                description_cell.setFlags(description_cell.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

                table.setItem(i, 0, variable_cell)
                table.setItem(i, 1, description_cell)

            # Настройка таблицы
            table.horizontalHeader().setStretchLastSection(True)
            table.setColumnWidth(0, 200)
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            table.verticalHeader().setVisible(False)

            table.setStyleSheet("""
                QTableWidget {
                    font-size: 10pt;
                    selection-background-color: #555;
                }
                QHeaderView::section {
                    padding: 8px;
                    font-weight: bold;
                    background-color: #3c3c3c;
                }
            """)

            category_layout.addWidget(table)
            tab_widget.addTab(category_widget, self._get_category_icon(category_name))

        layout.addWidget(tab_widget)

        # Инструкция по использованию
        instruction = QLabel(
            "💡 <b>Как использовать:</b><br>"
            "1. Создайте шаблон в Microsoft Word или другом редакторе<br>"
            "2. Вставьте переменные в нужных местах в формате <code>{{имя_переменной}}</code><br>"
            "3. Сохраните файл как .docx в папку <code>templates/</code><br>"
            "4. Переменные автоматически заменятся на данные при генерации"
        )
        instruction.setStyleSheet("""
            background-color: #333;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
            font-size: 10pt;
        """)
        instruction.setWordWrap(True)
        layout.addWidget(instruction)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)

        # Кнопка копирования всех переменных
        copy_button = QPushButton("📋 Копировать все переменные")
        copy_button.clicked.connect(lambda: self.copy_all_variables_to_clipboard())
        buttons.addButton(copy_button, QDialogButtonBox.ButtonRole.ActionRole)

        layout.addWidget(buttons)

        dialog.exec()

    def _get_category_title(self, category_name):
        """Получение заголовка категории на русском"""
        titles = {
            "student_variables": "Данные студента",
            "specialty_variables": "Данные специальности",
            "module_variables": "Данные модуля",
            "teacher_variables": "Данные преподавателя",
            "organization_variables": "Данные организации",
            "practice_leader_variables": "Руководитель практики",
            "production_practice_variables": "Производственная практика",
            "study_practice_variables": "Учебная практика",
            "date_time_variables": "Дата и время",
            "calculated_variables": "Вычисляемые поля"
        }
        return titles.get(category_name, category_name)

    def _get_category_icon(self, category_name):
        """Получение иконки для вкладки категории"""
        icons = {
            "student_variables": "👨‍🎓 Студент",
            "specialty_variables": "🎓 Специальность",
            "module_variables": "📚 Модуль",
            "teacher_variables": "👨‍🏫 Преподаватель",
            "organization_variables": "🏢 Организация",
            "practice_leader_variables": "👔 Руководитель",
            "production_practice_variables": "🏭 Производственная",
            "study_practice_variables": "📖 Учебная",
            "date_time_variables": "📅 Дата/время",
            "calculated_variables": "🧮 Вычисляемые"
        }
        return icons.get(category_name, category_name)

    def copy_all_variables_to_clipboard(self):
        """Копирование всех переменных в буфер обмена"""
        all_vars = self.doc_gen.get_flat_variable_list()
        # Форматируем переменные для шаблона
        formatted_vars = [f"{{{{{var}}}}}" for var in all_vars]
        clipboard_text = "\n".join(formatted_vars)

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text)

        QMessageBox.information(
            self,
            "Скопировано",
            f"Скопировано {len(all_vars)} переменных в буфер обмена.\n\n"
            "Теперь вы можете вставить их в свой шаблон."
        )

    def show_success_message(self, title, message, file_path=None):
        """Показать сообщение об успешной генерации с кнопкой открытия папки"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Information)

        if file_path and os.path.exists(os.path.dirname(file_path) if os.path.isfile(file_path) else file_path):
            open_button = msg.addButton('Открыть папку', QMessageBox.ButtonRole.ActionRole)
            msg.addButton('OK', QMessageBox.ButtonRole.AcceptRole)

            msg.exec()

            if msg.clickedButton() == open_button:
                import subprocess
                try:
                    if os.path.isfile(file_path):
                        folder = os.path.dirname(file_path)
                    else:
                        folder = file_path

                    if sys.platform == "win32":
                        os.startfile(folder)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", folder])
                    else:
                        subprocess.run(["xdg-open", folder])
                except Exception as e:
                    self.log_message(f"Не удалось открыть папку: {e}")
        else:
            msg.exec()

    def log_message(self, message):
        """Добавление сообщения в лог"""
        timestamp = QDateTime.currentDateTime().toString('hh:mm:ss')
        self.log_text.append(f"[{timestamp}] {message}")
        self.statusBar().showMessage(message, 3000)  # Показываем 3 секунды

        # Автопрокрутка вниз
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Устанавливаем иконку приложения
    app.setWindowIcon(QIcon.fromTheme('document'))

    window = PracticeManager()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

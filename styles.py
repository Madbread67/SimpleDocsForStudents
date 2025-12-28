dark_style = """
/* Основные стили */
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 11pt;
    border: none;
}

/* Кнопки */
QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 8px 16px;
    color: #e0e0e0;
    font-weight: 500;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #666;
}

QPushButton:pressed {
    background-color: #2a2a2a;
    border-color: #444;
}

QPushButton:disabled {
    background-color: #353535;
    color: #777;
    border-color: #444;
}

/* Специальные кнопки */
QPushButton[style*="green"] {
    background-color: #4CAF50;
    border-color: #45a049;
}

QPushButton[style*="blue"] {
    background-color: #2196F3;
    border-color: #1976D2;
}

QPushButton[style*="red"] {
    background-color: #f44336;
    border-color: #d32f2f;
}

/* Поля ввода */
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit {
    background-color: #353535;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 6px;
    color: #e0e0e0;
    selection-background-color: #555;
    min-height: 30px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDateEdit:focus {
    border: 2px solid #2196F3;
    padding: 5px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: url(down_arrow.png);
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #353535;
    border: 1px solid #555;
    color: #e0e0e0;
    selection-background-color: #555;
    outline: none;
}

/* Таблицы */
QTableWidget {
    background-color: #2d2d2d;
    alternate-background-color: #323232;
    gridline-color: #444;
    border: 1px solid #555;
    border-radius: 3px;
    selection-background-color: #555;
}

QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #444;
}

QTableWidget::item:selected {
    background-color: #555;
    color: white;
}

QHeaderView::section {
    background-color: #3c3c3c;
    padding: 8px;
    border: 1px solid #555;
    font-weight: bold;
    color: #e0e0e0;
}

QHeaderView::section:hover {
    background-color: #4a4a4a;
}

/* Вкладки */
QTabWidget::pane {
    border: 1px solid #555;
    background-color: #2d2d2d;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #3c3c3c;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    color: #e0e0e0;
}

QTabBar::tab:selected {
    background-color: #555;
    border-bottom: 2px solid #2196F3;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #4a4a4a;
}

/* Группы */
QGroupBox {
    border: 1px solid #555;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 15px;
    font-weight: bold;
    color: #e0e0e0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #e0e0e0;
}

/* Метки */
QLabel {
    color: #e0e0e0;
}

QLabel[style*="status"] {
    padding: 5px;
    border-radius: 3px;
    font-weight: bold;
}

/* Скроллбары */
QScrollBar:vertical {
    background-color: #353535;
    width: 15px;
    border-radius: 7px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #555;
    min-height: 20px;
    border-radius: 7px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #353535;
    height: 15px;
    border-radius: 7px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #555;
    min-width: 20px;
    border-radius: 7px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #666;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Статус бар */
QStatusBar {
    background-color: #3c3c3c;
    color: #aaa;
    border-top: 1px solid #555;
}

QStatusBar::item {
    border: none;
}

/* Диалоговые окна */
QDialog {
    background-color: #2d2d2d;
}

QMessageBox {
    background-color: #2d2d2d;
}

QMessageBox QLabel {
    color: #e0e0e0;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* Меню */
QMenuBar {
    background-color: #3c3c3c;
    color: #e0e0e0;
}

QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #555;
}

QMenu {
    background-color: #3c3c3c;
    border: 1px solid #555;
    color: #e0e0e0;
}

QMenu::item {
    padding: 5px 30px 5px 20px;
}

QMenu::item:selected {
    background-color: #555;
}

QMenu::separator {
    height: 1px;
    background-color: #555;
    margin: 5px 10px;
}

/* Splitter */
QSplitter::handle {
    background-color: #444;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #555;
}

QSplitter::handle:horizontal {
    width: 4px;
}

QSplitter::handle:vertical {
    height: 4px;
}

/* Progress bar */
QProgressBar {
    border: 1px solid #555;
    border-radius: 3px;
    text-align: center;
    color: #e0e0e0;
}

QProgressBar::chunk {
    background-color: #2196F3;
    border-radius: 3px;
}

/* Tooltip */
QToolTip {
    background-color: #353535;
    border: 1px solid #555;
    color: #e0e0e0;
    padding: 5px;
    border-radius: 3px;
    opacity: 240;
}

/* Checkbox */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #555;
    background-color: #353535;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    border: 2px solid #2196F3;
    background-color: #2196F3;
    border-radius: 3px;
    image: url(check.png);
}

/* Radio button */
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QRadioButton::indicator:unchecked {
    border: 2px solid #555;
    background-color: #353535;
    border-radius: 9px;
}

QRadioButton::indicator:checked {
    border: 2px solid #2196F3;
    background-color: #2196F3;
    border-radius: 9px;
}

/* Spin box */
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #444;
    border: 1px solid #555;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #555;
}

QSpinBox::up-arrow, QSpinBox::down-arrow {
    width: 8px;
    height: 8px;
}

/* Date edit */
QDateEdit::drop-down {
    border: none;
    width: 25px;
}

QDateEdit::down-arrow {
    image: url(calendar.png);
    width: 16px;
    height: 16px;
}

/* Текст */
QTextEdit {
    background-color: #353535;
    border: 1px solid #555;
    border-radius: 3px;
    padding: 5px;
    color: #e0e0e0;
    selection-background-color: #555;
}

QTextEdit:focus {
    border: 2px solid #2196F3;
    padding: 4px;
}

/* Формы */
QFormLayout {
    spacing: 10px;
}

/* Панели */
QFrame {
    border: 1px solid #555;
    border-radius: 4px;
    background-color: #2d2d2d;
}

QFrame[frameShape="4"] { /* HLine */
    max-height: 2px;
    background-color: #555;
    border: none;
}

QFrame[frameShape="5"] { /* VLine */
    max-width: 2px;
    background-color: #555;
    border: none;
}

/* Дерево */
QTreeView {
    background-color: #2d2d2d;
    alternate-background-color: #323232;
    border: 1px solid #555;
    border-radius: 3px;
}

QTreeView::item {
    padding: 5px;
    border-bottom: 1px solid #444;
}

QTreeView::item:selected {
    background-color: #555;
    color: white;
}

QTreeView::branch:closed:has-children {
    image: url(branch_closed.png);
}

QTreeView::branch:open:has-children {
    image: url(branch_open.png);
}

/* Список */
QListView {
    background-color: #2d2d2d;
    border: 1px solid #555;
    border-radius: 3px;
}

QListView::item {
    padding: 5px;
    border-bottom: 1px solid #444;
}

QListView::item:selected {
    background-color: #555;
    color: white;
}
"""

MAIN_STYLE = """
QMainWindow, QWidget {
    background-color: #f0f4f8;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #2d3748;
}

/* Sidebar */
#sidebar {
    background-color: #1a365d;
    min-width: 220px;
    max-width: 220px;
}

#sidebar QPushButton {
    background-color: transparent;
    color: #bee3f8;
    border: none;
    text-align: left;
    padding: 12px 20px;
    font-size: 13px;
    border-radius: 0;
}

#sidebar QPushButton:hover {
    background-color: #2a4a7f;
    color: white;
}

#sidebar QPushButton:checked {
    background-color: #2b6cb0;
    color: white;
    font-weight: bold;
    border-left: 4px solid #63b3ed;
}

#logo_label {
    color: white;
    font-size: 16px;
    font-weight: bold;
    padding: 20px;
    background-color: #1a365d;
    border-bottom: 1px solid #2a4a7f;
}

#school_name {
    color: #bee3f8;
    font-size: 11px;
    padding: 0px 20px 15px 20px;
}

/* Content area */
#content {
    background-color: #f0f4f8;
    padding: 0;
}

/* Page title */
#page_title {
    font-size: 22px;
    font-weight: bold;
    color: #1a365d;
    padding: 15px 25px 5px 25px;
}

/* Cards */
QFrame#card {
    background-color: white;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
}

/* Stat cards */
QFrame#stat_card {
    background-color: white;
    border-radius: 10px;
    border: 1px solid #e2e8f0;
    min-height: 100px;
}

/* Buttons */
QPushButton#btn_primary {
    background-color: #2b6cb0;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}

QPushButton#btn_primary:hover {
    background-color: #2c5282;
}

QPushButton#btn_success {
    background-color: #276749;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}

QPushButton#btn_success:hover {
    background-color: #22543d;
}

QPushButton#btn_danger {
    background-color: #c53030;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
}

QPushButton#btn_danger:hover {
    background-color: #9b2c2c;
}

QPushButton#btn_secondary {
    background-color: #e2e8f0;
    color: #2d3748;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
}

QPushButton#btn_secondary:hover {
    background-color: #cbd5e0;
}

/* Tables */
QTableWidget {
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f0f4f8;
    selection-background-color: #ebf8ff;
    selection-color: #2d3748;
    alternate-background-color: #f7fafc;
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #f0f4f8;
}

QHeaderView::section {
    background-color: #edf2f7;
    color: #4a5568;
    font-weight: bold;
    padding: 10px 12px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
}

/* Inputs */
QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit {
    background-color: white;
    border: 1px solid #cbd5e0;
    border-radius: 6px;
    padding: 8px 12px;
    color: #2d3748;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QTextEdit:focus {
    border: 2px solid #4299e1;
    outline: none;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

/* Labels */
QLabel#label_field {
    font-weight: bold;
    color: #4a5568;
    font-size: 12px;
}

/* Search */
QLineEdit#search_input {
    background-color: white;
    border: 1px solid #cbd5e0;
    border-radius: 20px;
    padding: 8px 16px;
    font-size: 13px;
}

/* Status badges */
QLabel#badge_valide {
    background-color: #c6f6d5;
    color: #276749;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#badge_attente {
    background-color: #fefcbf;
    color: #744210;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

QLabel#badge_rejete {
    background-color: #fed7d7;
    color: #742a2a;
    border-radius: 10px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: bold;
}

/* ScrollBar */
QScrollBar:vertical {
    background: #f0f4f8;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #cbd5e0;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #a0aec0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* Notifications badge */
#notif_badge {
    background-color: #e53e3e;
    color: white;
    border-radius: 10px;
    font-size: 10px;
    font-weight: bold;
    padding: 1px 5px;
    min-width: 18px;
    max-width: 18px;
    min-height: 18px;
    max-height: 18px;
}

QTabWidget::pane {
    border: 1px solid #e2e8f0;
    background-color: white;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #edf2f7;
    color: #4a5568;
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    color: #2b6cb0;
    font-weight: bold;
    border-bottom: 2px solid #2b6cb0;
}

QGroupBox {
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #4a5568;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}

QMessageBox {
    background-color: white;
}

QDialog {
    background-color: #f0f4f8;
}
"""

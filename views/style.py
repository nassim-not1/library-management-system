LIGHT_THEME_QSS = """
/* Global Font */
* {
    font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
    font-size: 14px;
    color: #111827;
}

QMainWindow, QDialog {
    background-color: #F3F4F6;
}

QLabel {
    color: #374151;
}

QLabel#pageTitle, QLabel#mainTitle {
    font-size: 26px;
    font-weight: 900;
    color: #1E293B; /* Slate 800 */
    padding: 10px 0px;
    margin-bottom: 10px;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #0F2F3A;
    border-right: 1px solid #B7CBD0;
}

QLabel#sidebarTitle {
    font-size: 22px;
    font-weight: 900;
    color: #FFFFFF;
    padding: 2px 8px 0px 8px;
    letter-spacing: 1px;
}

QLabel#sessionLabel {
    color: #B8D6DC;
    font-size: 12px;
    font-weight: 600;
    padding: 0px 8px 14px 8px;
    border-bottom: 1px solid #1F4B57;
}

QLabel#sidebarSectionLabel {
    color: #8FB6C1;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    padding: 8px 8px 3px 8px;
}

QScrollArea#sidebarScroll {
    background-color: transparent;
    border: none;
}

QPushButton[class="sidebarButton"] {
    background-color: transparent;
    color: #D7ECEF;
    border: none;
    text-align: left;
    padding: 9px 12px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 6px;
    border-left: 3px solid transparent;
}

QPushButton[class="sidebarButton"]:hover {
    background-color: #164A56;
    color: #FFFFFF;
    border-left: 3px solid #5CC8BE;
}

QPushButton[class="sidebarButton"][active="true"] {
    background-color: #DFF7F4;
    color: #0B2A33;
    border-left: 3px solid #14B8A6;
    font-weight: 800;
}

QPushButton#logoutButton {
    background-color: transparent;
    color: #FCA5A5;
    border: 1px solid #2B5964;
    text-align: left;
    padding: 9px 12px;
    margin: 6px 0px 0px 0px;
    font-size: 14px;
    font-weight: 700;
    border-radius: 6px;
}

QPushButton#logoutButton:hover {
    background-color: #7F1D1D;
    color: #FFFFFF;
    border: 1px solid #991B1B;
}

/* Main Content Containers */
QFrame#mainContainer {
    background-color: #F3F4F6;
}

QFrame#card {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
}

QFrame#formContainer {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    padding: 15px;
}

QLabel#statTitle {
    color: #6B7280;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
}

QLabel#statValue {
    color: #4F46E5; /* Indigo 600 */
    font-size: 32px;
    font-weight: 900;
}

QLabel#statDetail {
    color: #9CA3AF;
    font-size: 12px;
}

/* Inputs */
QLineEdit, QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 8px 12px;
    color: #111827;
    font-size: 14px;
    selection-background-color: #4F46E5;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #4F46E5;
    outline: none;
}

QLineEdit::placeholder {
    color: #9CA3AF;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    color: #374151;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #F9FAFB;
    border: 1px solid #9CA3AF;
}

QPushButton#primaryAction {
    background-color: #4F46E5;
    color: #FFFFFF;
    border: none;
}
QPushButton#primaryAction:hover { background-color: #4338CA; }

QPushButton#dangerAction {
    background-color: #EF4444;
    color: #FFFFFF;
    border: none;
}
QPushButton#dangerAction:hover { background-color: #DC2626; }

/* Table Widget */
QTableWidget {
    background-color: #FFFFFF;
    color: #111827;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    gridline-color: #F3F4F6;
    selection-background-color: #EEF2FF;
    selection-color: #111827;
    alternate-background-color: #F9FAFB;
    outline: 0;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #E5E7EB;
}

QHeaderView::section {
    background-color: #F9FAFB;
    color: #6B7280;
    padding: 12px 15px;
    border: none;
    border-bottom: 2px solid #E5E7EB;
    border-right: 1px solid #E5E7EB;
    font-weight: bold;
    font-size: 12px;
    text-transform: uppercase;
}

/* ScrollBar */
QScrollBar:vertical {
    background: #F3F4F6;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #CBD5E1;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover { background: #94A3B8; }

QMessageBox { background-color: #FFFFFF; }
QMessageBox QLabel { color: #111827; font-size: 14px; }
"""

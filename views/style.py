LIGHT_THEME_QSS = """
* {
    font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
    font-size: 14px;
    color: #111827;
}

QMainWindow, QDialog {
    background-color: #F6F8FB;
}

QStackedWidget#mainContainer {
    background-color: #F6F8FB;
}

QLabel {
    color: #334155;
}

QToolTip {
    background-color: #111827;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 6px 8px;
}

QLabel#pageTitle, QLabel#mainTitle {
    color: #0F172A;
    font-size: 28px;
    font-weight: 900;
    padding: 4px 0px 12px 0px;
}

QLabel#sectionTitle {
    color: #0F172A;
    font-size: 18px;
    font-weight: 800;
    padding-bottom: 4px;
}

QLabel#authErrorLabel {
    background-color: #FEF2F2;
    color: #991B1B;
    border: 1px solid #FECACA;
    border-radius: 8px;
    padding: 9px 11px;
    font-size: 13px;
    font-weight: 700;
}

/* Sidebar */
QFrame#sidebar {
    background-color: #0B2A33;
    border-right: 1px solid #D8E1EA;
}

QWidget#navContainer {
    background-color: #0B2A33;
}

QLabel#sidebarTitle {
    color: #FFFFFF;
    font-size: 22px;
    font-weight: 900;
    padding: 4px 10px 0px 10px;
    letter-spacing: 1px;
}

QLabel#sessionLabel {
    color: #B8DDE4;
    font-size: 12px;
    font-weight: 700;
    padding: 0px 10px 16px 10px;
    border-bottom: 1px solid #214955;
}

QLabel#sidebarSectionLabel {
    color: #9FD3DB;
    font-size: 11px;
    font-weight: 900;
    padding: 10px 10px 5px 10px;
    letter-spacing: 1px;
}

QFrame#sidebarSectionDivider {
    background-color: #214955;
    border: none;
    margin: 4px 10px 0px 10px;
}

QScrollArea#sidebarScroll {
    background-color: #0B2A33;
    border: none;
}

QScrollArea#contentScroll {
    background-color: transparent;
    border: none;
}

QPushButton[class="sidebarButton"] {
    background-color: transparent;
    color: #DBEEF2;
    border: 1px solid transparent;
    border-radius: 8px;
    text-align: left;
    padding: 10px 13px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton[class="sidebarButton"]:hover {
    background-color: #123D49;
    color: #FFFFFF;
    border: 1px solid #245C6B;
}

QPushButton[class="sidebarButton"]:focus {
    background-color: #123D49;
    color: #FFFFFF;
    border: 1px solid #9FD3DB;
}

QPushButton[class="sidebarButton"][active="true"] {
    background-color: #D9F4F1;
    color: #082A31;
    border: 1px solid #5CC8BE;
    font-weight: 900;
}

QPushButton[class="sidebarButton"][active="true"]:focus,
QPushButton[class="sidebarButton"][active="true"]:hover {
    background-color: #D9F4F1;
    color: #082A31;
    border: 1px solid #14B8A6;
}

QPushButton#logoutButton {
    background-color: #123742;
    color: #FCA5A5;
    border: 1px solid #2B5964;
    border-radius: 8px;
    text-align: left;
    padding: 10px 14px;
    font-size: 14px;
    font-weight: 800;
}

QPushButton#logoutButton:hover {
    background-color: #7F1D1D;
    color: #FFFFFF;
    border: 1px solid #B91C1C;
}

/* Cards and containers */
QFrame#card,
QFrame#formContainer,
QFrame#authCard {
    background-color: #FFFFFF;
    border: 1px solid #E5EAF0;
    border-radius: 8px;
}

QFrame#authCard {
    padding: 6px;
}

QLabel#statTitle {
    color: #64748B;
    font-size: 12px;
    font-weight: 900;
}

QLabel#statValue {
    color: #2563EB;
    font-size: 34px;
    font-weight: 900;
}

QLabel#statValueText {
    color: #2563EB;
    font-size: 18px;
    font-weight: 900;
}

QLabel#statDetail {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 600;
}

QLabel#detailFieldLabel {
    color: #64748B;
    font-size: 13px;
    font-weight: 900;
}

QLabel#detailFieldValue {
    color: #111827;
    font-size: 14px;
    font-weight: 600;
}

/* Inputs */
QLineEdit, QComboBox {
    background-color: #FFFFFF;
    color: #111827;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 9px 12px;
    selection-background-color: #2563EB;
    min-height: 20px;
}

QLineEdit:hover, QComboBox:hover {
    border: 1px solid #94A3B8;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #2563EB;
    background-color: #FFFFFF;
}

QLineEdit::placeholder {
    color: #94A3B8;
}

QComboBox::drop-down {
    width: 28px;
    border: none;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    color: #334155;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 800;
}

QPushButton:hover {
    background-color: #F8FAFC;
    border: 1px solid #94A3B8;
}

QPushButton:pressed {
    background-color: #E2E8F0;
}

QPushButton#primaryAction {
    background-color: #2563EB;
    color: #FFFFFF;
    border: 1px solid #2563EB;
}

QPushButton#primaryAction:hover {
    background-color: #1D4ED8;
    border: 1px solid #1D4ED8;
}

QPushButton#dangerAction {
    background-color: #DC2626;
    color: #FFFFFF;
    border: 1px solid #DC2626;
}

QPushButton#dangerAction:hover {
    background-color: #B91C1C;
    border: 1px solid #B91C1C;
}

QPushButton#linkButton {
    background-color: transparent;
    color: #2563EB;
    border: none;
    padding: 6px 8px;
    font-size: 13px;
    font-weight: 800;
}

QPushButton#linkButton:hover {
    color: #1D4ED8;
    background-color: #EFF6FF;
}

QPushButton#smallAction {
    padding: 3px 8px;
    font-size: 12px;
    font-weight: 800;
    border-radius: 6px;
}

QPushButton#bookInfoAction {
    background-color: #EEF2FF;
    color: #3730A3;
    border: 1px solid #A5B4FC;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 900;
    border-radius: 6px;
}

QPushButton#bookInfoAction:hover {
    background-color: #E0E7FF;
    border: 1px solid #6366F1;
}

/* Tables */
QTableWidget {
    background-color: #FFFFFF;
    color: #111827;
    border: 1px solid #E5EAF0;
    border-radius: 8px;
    gridline-color: transparent;
    selection-background-color: #DBEAFE;
    selection-color: #0F172A;
    alternate-background-color: #F8FAFC;
    outline: 0;
}

QTableWidget::item {
    padding: 8px 10px;
    border-bottom: 1px solid #EEF2F7;
}

QTableWidget::item:hover {
    background-color: #F1F5F9;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    padding: 11px 12px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
    border-right: 1px solid #EEF2F7;
    font-weight: 900;
    font-size: 12px;
}

/* Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 9px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    border-radius: 4px;
    min-height: 36px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

QScrollBar:horizontal {
    background: transparent;
    height: 9px;
    margin: 2px;
}

QScrollBar::handle:horizontal {
    background: #CBD5E1;
    border-radius: 4px;
    min-width: 36px;
}

QScrollBar::add-line,
QScrollBar::sub-line,
QScrollBar::add-page,
QScrollBar::sub-page {
    background: transparent;
    border: none;
    width: 0px;
    height: 0px;
}

QMessageBox {
    background-color: #FFFFFF;
}

QMessageBox QLabel {
    color: #111827;
    font-size: 14px;
}
"""

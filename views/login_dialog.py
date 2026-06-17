from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from controllers.auth_controller import AuthController
from views.register_dialog import RegisterDialog


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accueil")
        self.setFixedSize(420, 420)
        self.auth_controller = AuthController()
        self.authenticated_user = None
        self.setup_ui()

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        return shadow

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        form_frame = QFrame()
        form_frame.setObjectName("formContainer")
        form_frame.setGraphicsEffect(self.create_shadow())
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        title_label = QLabel("Accueil")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        form_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.login)
        self.password_input.textChanged.connect(self.clear_error)
        form_layout.addWidget(self.password_input)

        self.error_label = QLabel("")
        self.error_label.setObjectName("authErrorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        form_layout.addWidget(self.error_label)

        form_layout.addStretch()

        btn_layout = QHBoxLayout()
        self.btn_quit = QPushButton("Annuler")
        self.btn_quit.clicked.connect(self.reject)

        self.btn_login = QPushButton("Se connecter")
        self.btn_login.setObjectName("primaryAction")
        self.btn_login.clicked.connect(self.login)

        btn_layout.addWidget(self.btn_quit)
        btn_layout.addWidget(self.btn_login)
        form_layout.addLayout(btn_layout)
        
        form_layout.addSpacing(10)
        
        self.btn_register = QPushButton("Pas encore de compte ? Créer un compte")
        self.btn_register.setStyleSheet("QPushButton { background: transparent; color: #4F46E5; border: none; font-weight: 600; font-size: 13px; } QPushButton:hover { text-decoration: underline; background: transparent; border: none; }")
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.clicked.connect(self.open_register)
        form_layout.addWidget(self.btn_register, alignment=Qt.AlignCenter)

        main_layout.addWidget(form_frame)

    def show_error(self, message, focus_widget=None):
        self.password_input.blockSignals(True)
        self.password_input.clear()
        self.password_input.blockSignals(False)
        self.error_label.setText(message)
        self.error_label.show()
        if focus_widget:
            focus_widget.setFocus()

    def clear_error(self):
        self.error_label.clear()
        self.error_label.hide()

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("Veuillez saisir le nom d'utilisateur et le mot de passe.", self.username_input)
            return

        try:
            user = self.auth_controller.authenticate(username, password)
        except Exception as e:
            self.show_error(f"Authentification impossible : {e}", self.password_input)
            return

        if not user:
            self.show_error("Identifiants incorrects. Verifiez le nom d'utilisateur et le mot de passe.", self.password_input)
            return

        self.clear_error()
        self.authenticated_user = user
        self.accept()

    def open_register(self):
        dialog = RegisterDialog(self.auth_controller, self)
        if dialog.exec() == QDialog.Accepted and dialog.created_user:
            self.authenticated_user = dialog.created_user
            self.accept()

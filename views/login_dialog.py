from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from controllers.auth_controller import AuthController
from views.register_dialog import RegisterDialog


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Accueil")
        self.setMinimumSize(420, 430)
        self.resize(460, 460)
        self.auth_controller = AuthController()
        self.authenticated_user = None
        self.setup_ui()

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(15, 23, 42, 35))
        shadow.setOffset(0, 10)
        return shadow

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 28, 28, 28)

        form_frame = QFrame()
        form_frame.setObjectName("authCard")
        form_frame.setGraphicsEffect(self.create_shadow())
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(26, 24, 26, 24)
        form_layout.setSpacing(16)

        title_label = QLabel("Accueil")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.username_input.setClearButtonEnabled(True)
        form_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setClearButtonEnabled(True)
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
        btn_layout.setSpacing(10)
        self.btn_quit = QPushButton("Annuler")
        self.btn_quit.setMinimumHeight(40)
        self.btn_quit.clicked.connect(self.reject)

        self.btn_login = QPushButton("Se connecter")
        self.btn_login.setObjectName("primaryAction")
        self.btn_login.setMinimumHeight(40)
        self.btn_login.clicked.connect(self.login)

        btn_layout.addWidget(self.btn_quit)
        btn_layout.addWidget(self.btn_login)
        form_layout.addLayout(btn_layout)
        
        form_layout.addSpacing(10)
        
        self.btn_register = QPushButton("Pas encore de compte ? Créer un compte")
        self.btn_register.setObjectName("linkButton")
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

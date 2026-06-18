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


class RegisterDialog(QDialog):
    def __init__(self, auth_controller, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Creation de compte")
        self.setMinimumSize(420, 400)
        self.resize(460, 430)
        self.auth_controller = auth_controller
        self.created_user = None
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

        title_label = QLabel("Creer un compte")
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
        form_layout.addWidget(self.password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmer le mot de passe")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setClearButtonEnabled(True)
        self.confirm_password_input.returnPressed.connect(self.create_account)
        form_layout.addWidget(self.confirm_password_input)

        form_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setMinimumHeight(40)
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_create = QPushButton("Creer")
        self.btn_create.setObjectName("primaryAction")
        self.btn_create.setMinimumHeight(40)
        self.btn_create.clicked.connect(self.create_account)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_create)
        form_layout.addLayout(btn_layout)

        main_layout.addWidget(form_frame)

    def create_account(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Le nom d'utilisateur et le mot de passe sont obligatoires.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas.")
            self.confirm_password_input.clear()
            self.confirm_password_input.setFocus()
            return

        try:
            self.created_user = self.auth_controller.create_account(username, password)
            QMessageBox.information(self, "Succes", "Compte cree avec succes.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erreur", str(e))

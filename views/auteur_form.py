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


class AuteurForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un auteur")
        self.setFixedSize(420, 360)
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
        form_frame.setObjectName("mainContainer")
        form_frame.setGraphicsEffect(self.create_shadow())
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        title_label = QLabel("Nouvel Auteur")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de l'auteur *")
        form_layout.addWidget(self.nom_input)

        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prenom")
        form_layout.addWidget(self.prenom_input)

        self.nationalite_input = QLineEdit()
        self.nationalite_input.setPlaceholderText("Nationalite")
        self.nationalite_input.returnPressed.connect(self.valider)
        form_layout.addWidget(self.nationalite_input)

        form_layout.addStretch()

        btn_layout = QHBoxLayout()
        self.btn_annuler = QPushButton("Annuler")
        self.btn_annuler.clicked.connect(self.reject)

        self.btn_valider = QPushButton("Valider")
        self.btn_valider.setObjectName("primaryAction")
        self.btn_valider.clicked.connect(self.valider)

        btn_layout.addWidget(self.btn_annuler)
        btn_layout.addWidget(self.btn_valider)
        form_layout.addLayout(btn_layout)

        main_layout.addWidget(form_frame)

    def valider(self):
        if not self.nom_input.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom de l'auteur est obligatoire.")
            return

        self.accept()

    def get_data(self):
        return {
            "nom": self.nom_input.text().strip(),
            "prenom": self.prenom_input.text().strip(),
            "nationalite": self.nationalite_input.text().strip(),
        }

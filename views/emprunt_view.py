from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

class EmpruntView(QDialog):
    def __init__(self, parent=None, titre_livre=""):
        super().__init__(parent)
        self.setWindowTitle("Emprunter un livre")
        self.setFixedSize(400, 350)
        self.titre_livre = titre_livre
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
        
        title_label = QLabel("Dossier d'Emprunt")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)

        info_label = QLabel(f"Livre : {self.titre_livre}")
        info_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #03DAC6; margin-bottom: 10px;")
        form_layout.addWidget(info_label)

        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom de l'utilisateur *")
        form_layout.addWidget(self.nom_input)

        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prénom de l'utilisateur")
        form_layout.addWidget(self.prenom_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (optionnel)")
        form_layout.addWidget(self.email_input)

        form_layout.addStretch()

        # Boutons
        btn_layout = QHBoxLayout()
        self.btn_valider = QPushButton("✅ Confirmer")
        self.btn_valider.setObjectName("primaryAction")
        self.btn_valider.clicked.connect(self.valider)
        
        self.btn_annuler = QPushButton("❌ Annuler")
        self.btn_annuler.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_annuler)
        btn_layout.addWidget(self.btn_valider)
        
        form_layout.addLayout(btn_layout)
        main_layout.addWidget(form_frame)

    def valider(self):
        nom = self.nom_input.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de l'utilisateur est obligatoire.")
            return
        self.accept()

    def get_data(self):
        return {
            "nom": self.nom_input.text().strip(),
            "prenom": self.prenom_input.text().strip(),
            "email": self.email_input.text().strip()
        }

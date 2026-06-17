from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QGraphicsDropShadowEffect,
                               QComboBox)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt

class LivreForm(QDialog):
    def __init__(self, parent=None, livre_data=None, auteurs=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un livre" if not livre_data else "Modifier le livre")
        self.setFixedSize(480, 450)
        self.livre_data = livre_data
        self.auteurs = auteurs or []
        
        self.setup_ui()
        if self.livre_data:
            self.load_data()

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
        
        # Title
        title_label = QLabel("Nouvel Ouvrage" if not self.livre_data else "Éditer l'Ouvrage")
        title_label.setObjectName("mainTitle")
        title_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title_label)

        # Fields
        self.titre_input = QLineEdit()
        self.titre_input.setPlaceholderText("Titre du livre *")
        form_layout.addWidget(self.titre_input)

        self.auteur_input = QComboBox()
        self.auteur_input.setPlaceholderText("Choisir un auteur *")
        for auteur in self.auteurs:
            label = str(auteur.get("auteur", "")).strip()
            if not label:
                label = str(auteur.get("nom", "")).strip()
            self.auteur_input.addItem(label, str(auteur.get("id_auteur", "")))
        self.auteur_input.setEnabled(bool(self.auteurs))
        form_layout.addWidget(self.auteur_input)

        info_label = QLabel("Si l'auteur du livre n'existe pas, ajoutez d'abord l'auteur dans la section Auteurs.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #B0B0B0; font-size: 12px;")
        form_layout.addWidget(info_label)

        self.categorie_input = QLineEdit()
        self.categorie_input.setPlaceholderText("Catégorie")
        form_layout.addWidget(self.categorie_input)

        self.annee_input = QLineEdit()
        self.annee_input.setPlaceholderText("Année de publication")
        form_layout.addWidget(self.annee_input)

        form_layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_valider = QPushButton("✅ Valider")
        self.btn_valider.setObjectName("primaryAction")
        self.btn_valider.clicked.connect(self.valider)
        
        self.btn_annuler = QPushButton("❌ Annuler")
        self.btn_annuler.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_annuler)
        btn_layout.addWidget(self.btn_valider)
        
        form_layout.addLayout(btn_layout)
        main_layout.addWidget(form_frame)

    def load_data(self):
        self.titre_input.setText(str(self.livre_data.get('titre', '')))
        id_auteur = str(self.livre_data.get('id_auteur', '')).strip()
        index = self.auteur_input.findData(id_auteur)
        if index < 0:
            index = self.auteur_input.findText(str(self.livre_data.get('auteur', '')).strip())
        if index >= 0:
            self.auteur_input.setCurrentIndex(index)
        self.categorie_input.setText(str(self.livre_data.get('categorie', '')))
        self.annee_input.setText(str(self.livre_data.get('annee', '')))

    def valider(self):
        titre = self.titre_input.text().strip()
        auteur = self.auteur_input.currentData()
        
        if not titre or not auteur:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir les champs obligatoires (Titre et Auteur).")
            return
            
        self.accept()

    def get_data(self):
        return {
            "titre": self.titre_input.text().strip(),
            "id_auteur": str(self.auteur_input.currentData()).strip(),
            "auteur": self.auteur_input.currentText().strip(),
            "categorie": self.categorie_input.text().strip(),
            "annee": self.annee_input.text().strip()
        }

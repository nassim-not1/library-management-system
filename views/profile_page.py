from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from controllers.profile_controller import ProfileController
from controllers.auth_controller import AuthController

class ProfilePage(QWidget):
    def __init__(self, parent_window, compte):
        super().__init__()
        self.parent_window = parent_window
        self.compte = compte
        self.id_compte = str(compte.get("id_compte", ""))
        self.username = str(compte.get("username", ""))
        
        self.profile_controller = ProfileController()
        self.auth_controller = AuthController()

        self.setup_ui()
        self.load_profile()

    def setup_ui(self):
        # Layout principal de la page (sans marges)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Zone de défilement pour tout le contenu
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Widget contenu dans la scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)

        lbl_title = QLabel("Mon Profil")
        lbl_title.setObjectName("pageTitle")
        layout.addWidget(lbl_title)

        # Container for Profile Info
        profile_frame = QFrame()
        profile_frame.setObjectName("formContainer")
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setSpacing(20)

        lbl_section1 = QLabel("Informations Personnelles")
        lbl_section1.setStyleSheet("font-weight: bold; font-size: 18px; color: #1E293B; margin-bottom: 10px;")
        profile_layout.addWidget(lbl_section1)

        form1 = QFormLayout()
        form1.setSpacing(15)
        
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Nom (obligatoire)")
        
        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Prénom")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Adresse Email")

        form1.addRow("Nom :", self.nom_input)
        form1.addRow("Prénom :", self.prenom_input)
        form1.addRow("Email :", self.email_input)
        profile_layout.addLayout(form1)
        
        btn_save_profile = QPushButton("Enregistrer les modifications")
        btn_save_profile.setObjectName("primaryAction")
        btn_save_profile.setFixedWidth(250)
        btn_save_profile.clicked.connect(self.save_profile)
        profile_layout.addWidget(btn_save_profile, alignment=Qt.AlignRight)

        layout.addWidget(profile_frame)

        # Container for Security
        security_frame = QFrame()
        security_frame.setObjectName("formContainer")
        security_layout = QVBoxLayout(security_frame)
        security_layout.setSpacing(20)

        lbl_section2 = QLabel("Sécurité")
        lbl_section2.setStyleSheet("font-weight: bold; font-size: 18px; color: #1E293B; margin-bottom: 10px;")
        security_layout.addWidget(lbl_section2)

        form2 = QFormLayout()
        form2.setSpacing(15)

        self.old_pwd_input = QLineEdit()
        self.old_pwd_input.setPlaceholderText("Mot de passe actuel")
        self.old_pwd_input.setEchoMode(QLineEdit.Password)

        self.new_pwd_input = QLineEdit()
        self.new_pwd_input.setPlaceholderText("Nouveau mot de passe")
        self.new_pwd_input.setEchoMode(QLineEdit.Password)

        self.confirm_pwd_input = QLineEdit()
        self.confirm_pwd_input.setPlaceholderText("Confirmer le nouveau mot de passe")
        self.confirm_pwd_input.setEchoMode(QLineEdit.Password)

        form2.addRow("Ancien mot de passe :", self.old_pwd_input)
        form2.addRow("Nouveau mot de passe :", self.new_pwd_input)
        form2.addRow("Confirmation :", self.confirm_pwd_input)
        security_layout.addLayout(form2)

        btn_save_pwd = QPushButton("Modifier le mot de passe")
        btn_save_pwd.setObjectName("dangerAction") 
        btn_save_pwd.setFixedWidth(250)
        btn_save_pwd.clicked.connect(self.save_password)
        security_layout.addWidget(btn_save_pwd, alignment=Qt.AlignRight)

        layout.addWidget(security_frame)
        layout.addStretch()

    def refresh(self):
        self.load_profile()

    def load_profile(self):
        profile = self.profile_controller.get_profile(self.id_compte)
        if profile:
            self.nom_input.setText(profile.get("nom", ""))
            self.prenom_input.setText(profile.get("prenom", ""))
            self.email_input.setText(profile.get("email", ""))
        else:
            self.nom_input.setText(self.username)

    def save_profile(self):
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        email = self.email_input.text().strip()

        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return

        try:
            self.profile_controller.update_profile(self.id_compte, nom, prenom, email, self.username)
            QMessageBox.information(self, "Succès", "Votre profil a été mis à jour.")
            if hasattr(self.parent_window, "update_session_info_label"):
                self.parent_window.update_session_info_label(nom)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur : {e}")

    def save_password(self):
        old_pwd = self.old_pwd_input.text()
        new_pwd = self.new_pwd_input.text()
        confirm_pwd = self.confirm_pwd_input.text()

        if not old_pwd or not new_pwd or not confirm_pwd:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs de mot de passe.")
            return

        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "Erreur", "Les nouveaux mots de passe ne correspondent pas.")
            return

        try:
            self.auth_controller.update_password(self.id_compte, old_pwd, new_pwd)
            QMessageBox.information(self, "Succès", "Votre mot de passe a été modifié avec succès.")
            self.old_pwd_input.clear()
            self.new_pwd_input.clear()
            self.confirm_pwd_input.clear()
        except ValueError as ve:
            QMessageBox.warning(self, "Erreur", str(ve))
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite : {e}")

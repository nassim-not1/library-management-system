from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLineEdit, QMessageBox, QLabel, QFrame, 
                               QGraphicsDropShadowEffect, QStackedWidget, QComboBox, QScrollArea)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication
from controllers.livre_controller import LivreController
from controllers.emprunt_controller import EmpruntController
from controllers.auth_controller import AuthController
from controllers.profile_controller import ProfileController
from views.profile_page import ProfilePage

def create_shadow():
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setColor(QColor(0, 0, 0, 30))
    shadow.setOffset(0, 4)
    return shadow

class BasePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.controller = main_window.controller
        self.emprunt_controller = main_window.emprunt_controller
        self.auth_controller = main_window.auth_controller
        self.current_user = main_window.current_user
        self.is_admin = main_window.is_admin

    def refresh(self):
        pass

class DashboardPage(BasePage):
    def __init__(self, main_window):
        super().__init__(main_window)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel("Tableau de Bord")
        lbl_title.setObjectName("pageTitle")
        layout.addWidget(lbl_title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.content_widget = QWidget()
        self.grid = QGridLayout(self.content_widget)
        self.grid.setSpacing(20)
        self.scroll.setWidget(self.content_widget)
        layout.addWidget(self.scroll)

    def create_card(self, indicateur, valeur, detail):
        card = QFrame()
        card.setObjectName("card")
        card.setGraphicsEffect(create_shadow())
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        lbl_ind = QLabel(indicateur)
        lbl_ind.setObjectName("statTitle")
        lbl_val = QLabel(str(valeur))
        lbl_val.setObjectName("statValue")
        lbl_val.setAlignment(Qt.AlignCenter)
        lbl_det = QLabel(detail)
        lbl_det.setObjectName("statDetail")
        lbl_det.setAlignment(Qt.AlignCenter)
        lbl_det.setWordWrap(True)
        
        card_layout.addWidget(lbl_ind)
        card_layout.addWidget(lbl_val)
        card_layout.addWidget(lbl_det)
        
        card.setMinimumHeight(130)
        card.setMaximumHeight(160)
        return card

    def is_livre_emprunte(self, livre):
        statut = str(livre.get("disponibilite", livre.get("statut", ""))).lower()
        return "emprunt" in statut

    def refresh(self):
        for i in reversed(range(self.grid.count())): 
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        livres = self.controller.get_all_livres()
        auteurs = self.controller.get_all_auteurs()
        popular = self.emprunt_controller.get_livres_plus_empruntes()
        active_all = self.emprunt_controller.get_livres_empruntes()
        my_active = self.emprunt_controller.get_livres_empruntes_pour_compte(self.current_user)
        retards_all = self.emprunt_controller.get_livres_en_retard()
        my_retards = self.emprunt_controller.get_livres_en_retard_pour_compte(self.current_user)
        my_history = self.emprunt_controller.get_historique_emprunts_pour_compte(self.current_user)

        total_livres = len(livres)
        livres_disponibles = len([l for l in livres if not self.is_livre_emprunte(l)])
        taux_dispo = 0 if total_livres == 0 else round((livres_disponibles / total_livres) * 100)
        top_livre = popular[0] if popular else None
        top_livre_text = top_livre.get("titre", "-") if top_livre else "-"
        top_livre_det = f"{top_livre.get('nombre_emprunts', 0)} emprunts" if top_livre else "Aucun emprunt"

        data = []
        if self.is_admin:
            accounts = self.auth_controller.get_accounts()
            data = [
                ("Livres", total_livres, f"{livres_disponibles} dispo, {len(active_all)} empruntés"),
                ("Auteurs", len(auteurs), "Auteurs disponibles"),
                ("Comptes", len(accounts), "Utilisateurs enregistrés"),
                ("Emprunts actifs", len(active_all), "Tous les livres empruntés"),
                ("Livres en retard", len(retards_all), "Dépassant la limite"),
                ("Mes emprunts", len(my_active), "Vos emprunts actuels"),
                ("Mes retards", len(my_retards), "Vos livres en retard"),
                ("Disponibilité", f"{taux_dispo}%", "Part des livres disponibles"),
                ("Le plus emprunté", top_livre_text, top_livre_det)
            ]
        else:
            data = [
                ("Livres disponibles", livres_disponibles, "Livres que vous pouvez emprunter"),
                ("Mes emprunts actifs", len(my_active), "Vos emprunts actuels"),
                ("Mes retards", len(my_retards), "Livres à retourner"),
                ("Historique personnel", len(my_history), "Tous vos emprunts"),
                ("Catalogue", total_livres, f"{len(auteurs)} auteurs"),
                ("Disponibilité", f"{taux_dispo}%", "Part des livres disponibles"),
                ("Le plus emprunté", top_livre_text, top_livre_det)
            ]

        row, col = 0, 0
        for ind, val, det in data:
            self.grid.addWidget(self.create_card(ind, val, det), row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

class BaseTablePage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("pageTitle")
        self.layout.addWidget(lbl_title)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher...")
        self.search_input.textChanged.connect(self.on_search)
        self.layout.addWidget(self.search_input)
        
        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setGraphicsEffect(create_shadow())
        self.layout.addWidget(self.table)
        
        self.action_layout = QHBoxLayout()
        self.action_layout.setContentsMargins(0, 5, 10, 10)
        self.layout.addLayout(self.action_layout)
        
        self.current_data = []
        self.columns = []

    def set_columns(self, columns):
        self.columns = columns
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels([c[1] for c in columns])
        
    def load_data(self, data):
        self.current_data = data
        self.populate_table(data)
        
    def populate_table(self, data):
        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(data):
            self.table.insertRow(row_idx)
            for col_idx, (field, _) in enumerate(self.columns):
                item = QTableWidgetItem(str(row_data.get(field, "")))
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if field == "statut":
                    statut_text = str(row_data.get("statut", "")).lower()
                    if "emprunt" in statut_text or "retard" in statut_text:
                        item.setForeground(QColor("#EF4444"))
                    else:
                        item.setForeground(QColor("#10B981"))
                self.table.setItem(row_idx, col_idx, item)

    def get_selected_id(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Attention", "Aucun élément sélectionné.")
            return None
        return self.table.item(selected[0].row(), 0).text()

    def on_search(self, text):
        if not text:
            self.populate_table(self.current_data)
            return
        text = text.lower()
        searchable_fields = ["titre", "auteur", "categorie", "description", "mots_cles", "emprunteur", "nom", "prenom", "nationalite", "username"]
        filtered = [
            l for l in self.current_data
            if any(text in str(l.get(f, "")).lower() for f in searchable_fields)
        ]
        self.populate_table(filtered)

class ManageBooksPage(BaseTablePage):
    def __init__(self, main_window):
        super().__init__(main_window, "📚 Tous les livres")
        self.set_columns([
            ("id_livre", "ID"), ("titre", "Titre"), ("auteur", "Auteur"),
            ("categorie", "Categorie"), ("annee", "Annee"), ("description", "Description"),
            ("mots_cles", "Mots cles"), ("statut", "Statut")
        ])
        
        if self.is_admin:
            self.form_frame = QFrame()
            self.form_frame.setObjectName("formContainer")
            form_layout = QVBoxLayout(self.form_frame)
            form_layout.setContentsMargins(15, 15, 15, 15)
            
            inputs_layout = QHBoxLayout()
            
            self.inp_titre = QLineEdit()
            self.inp_titre.setPlaceholderText("Titre")
            self.inp_auteur = QComboBox()
            self.inp_categorie = QLineEdit()
            self.inp_categorie.setPlaceholderText("Catégorie")
            self.inp_annee = QLineEdit()
            self.inp_annee.setPlaceholderText("Année")
            self.inp_description = QLineEdit()
            self.inp_description.setPlaceholderText("Description")
            self.inp_mots_cles = QLineEdit()
            self.inp_mots_cles.setPlaceholderText("Mots cles")
            
            inputs_layout.addWidget(self.inp_titre)
            inputs_layout.addWidget(self.inp_auteur)
            inputs_layout.addWidget(self.inp_categorie)
            inputs_layout.addWidget(self.inp_annee)
            form_layout.addLayout(inputs_layout)

            details_layout = QHBoxLayout()
            details_layout.addWidget(self.inp_description)
            details_layout.addWidget(self.inp_mots_cles)
            form_layout.addLayout(details_layout)
            
            self.layout.insertWidget(2, self.form_frame)
            
            btn_add = QPushButton("✨ Ajouter")
            btn_add.setObjectName("primaryAction")
            btn_add.clicked.connect(self.on_add)
            
            btn_update = QPushButton("✏️ Modifier")
            btn_update.clicked.connect(self.on_update)
            
            btn_delete = QPushButton("🗑️ Supprimer")
            btn_delete.setObjectName("dangerAction")
            btn_delete.clicked.connect(self.on_delete)
            
            btns_layout = QHBoxLayout()
            btns_layout.addWidget(btn_add)
            btns_layout.addWidget(btn_update)
            btns_layout.addWidget(btn_delete)
            form_layout.addLayout(btns_layout)
            
            self.table.itemSelectionChanged.connect(self.on_selection)
            
        self.action_layout.addStretch()
        btn_borrow = QPushButton("📤 Emprunter")
        btn_borrow.clicked.connect(self.on_borrow)
        self.action_layout.addWidget(btn_borrow)

    def refresh(self):
        if self.is_admin:
            self.inp_auteur.clear()
            for a in self.controller.get_all_auteurs():
                label = str(a.get("auteur", a.get("nom", ""))).strip()
                self.inp_auteur.addItem(label, str(a.get("id_auteur", "")))
        self.load_data(self.controller.get_all_livres())

    def _table_text(self, row, column):
        item = self.table.item(row, column)
        return item.text() if item else ""

    def on_selection(self):
        if not self.is_admin: return
        selected = self.table.selectedItems()
        if not selected: return
        row = selected[0].row()
        self.inp_titre.setText(self._table_text(row, 1))
        self.inp_categorie.setText(self._table_text(row, 3))
        self.inp_annee.setText(self._table_text(row, 4))
        self.inp_description.setText(self._table_text(row, 5))
        self.inp_mots_cles.setText(self._table_text(row, 6))
        auteur_text = self._table_text(row, 2)
        idx = self.inp_auteur.findText(auteur_text)
        if idx >= 0: self.inp_auteur.setCurrentIndex(idx)

    def on_add(self):
        try:
            self.controller.add_livre(
                self.inp_titre.text(), self.inp_auteur.currentData(),
                self.inp_categorie.text(), self.inp_annee.text(),
                self.inp_description.text(), self.inp_mots_cles.text()
            )
            self.refresh()
            QMessageBox.information(self, "Succès", "Livre ajouté.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def on_update(self):
        book_id = self.get_selected_id()
        if not book_id: return
        try:
            self.controller.update_livre(
                book_id, self.inp_titre.text(), self.inp_auteur.currentData(),
                self.inp_categorie.text(), self.inp_annee.text(),
                self.inp_description.text(), self.inp_mots_cles.text()
            )
            self.refresh()
            QMessageBox.information(self, "Succès", "Livre modifié.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def on_delete(self):
        book_id = self.get_selected_id()
        if not book_id: return
        reply = QMessageBox.question(self, 'Confirmation', "Supprimer ce livre ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_livre(book_id)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def on_borrow(self):
        book_id = self.get_selected_id()
        if not book_id: return
        try:
            self.emprunt_controller.emprunter_livre_pour_compte(book_id, self.current_user)
            self.refresh()
            QMessageBox.information(self, "Succès", "Livre emprunté.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

class RecommendationsPage(BaseTablePage):
    def __init__(self, main_window):
        super().__init__(main_window, "Recommandations")
        self.set_columns([
            ("id_livre", "ID"), ("titre", "Titre"), ("auteur", "Auteur"),
            ("categorie", "Categorie"), ("annee", "Annee"),
            ("score_recommandation", "Similarite"), ("description", "Description"),
            ("mots_cles", "Mots cles"), ("statut", "Statut")
        ])

        selector_frame = QFrame()
        selector_frame.setObjectName("formContainer")
        selector_layout = QHBoxLayout(selector_frame)
        selector_layout.setContentsMargins(15, 15, 15, 15)

        self.book_combo = QComboBox()
        self.book_combo.setMinimumWidth(320)
        selector_layout.addWidget(self.book_combo, 1)

        btn_recommend = QPushButton("Recommander")
        btn_recommend.setObjectName("primaryAction")
        btn_recommend.clicked.connect(self.on_recommend)
        selector_layout.addWidget(btn_recommend)

        btn_clear = QPushButton("Effacer")
        btn_clear.clicked.connect(lambda _: self.load_data([]))
        selector_layout.addWidget(btn_clear)

        self.layout.insertWidget(1, selector_frame)
        self.action_layout.addStretch()

    def refresh(self):
        current_id = self.book_combo.currentData()
        self.book_combo.clear()

        for livre in self.controller.get_all_livres():
            title = str(livre.get("titre", "")).strip()
            author = str(livre.get("auteur", "")).strip()
            label = f"{title} - {author}" if author else title
            self.book_combo.addItem(label, str(livre.get("id_livre", "")))

        if current_id:
            index = self.book_combo.findData(current_id)
            if index >= 0:
                self.book_combo.setCurrentIndex(index)

        if not self.current_data:
            self.load_data([])

    def on_recommend(self):
        book_id = self.book_combo.currentData()
        if not book_id:
            QMessageBox.warning(self, "Attention", "Aucun livre selectionne.")
            return

        try:
            recommendations = self.controller.get_livres_recommandes(book_id)
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))
            return

        if not recommendations:
            QMessageBox.information(self, "Recommandations", "Aucun livre similaire trouve.")
            self.load_data([])
            return

        self.load_data(recommendations)

class ManageAuthorsPage(BaseTablePage):
    def __init__(self, main_window):
        super().__init__(main_window, "Auteurs")
        self.set_columns([("id_auteur", "ID"), ("nom", "Nom"), ("prenom", "Prénom"), ("nationalite", "Nationalité")])
        
        if self.is_admin:
            self.form_frame = QFrame()
            self.form_frame.setObjectName("formContainer")
            form_layout = QVBoxLayout(self.form_frame)
            form_layout.setContentsMargins(15, 15, 15, 15)
            
            inputs_layout = QHBoxLayout()
            self.inp_nom = QLineEdit()
            self.inp_nom.setPlaceholderText("Nom")
            self.inp_prenom = QLineEdit()
            self.inp_prenom.setPlaceholderText("Prénom")
            self.inp_nationalite = QLineEdit()
            self.inp_nationalite.setPlaceholderText("Nationalité")
            
            inputs_layout.addWidget(self.inp_nom)
            inputs_layout.addWidget(self.inp_prenom)
            inputs_layout.addWidget(self.inp_nationalite)
            form_layout.addLayout(inputs_layout)
            
            self.layout.insertWidget(2, self.form_frame)
            
            btn_add = QPushButton("✨ Ajouter")
            btn_add.setObjectName("primaryAction")
            btn_add.clicked.connect(self.on_add)

            btn_delete = QPushButton("Supprimer")
            btn_delete.setObjectName("dangerAction")
            btn_delete.clicked.connect(self.on_delete)
            
            btns_layout = QHBoxLayout()
            btns_layout.addWidget(btn_add)
            btns_layout.addWidget(btn_delete)
            form_layout.addLayout(btns_layout)
            
        self.action_layout.addStretch()

    def refresh(self):
        self.load_data(self.controller.get_all_auteurs())

    def on_add(self):
        try:
            self.controller.add_auteur(self.inp_nom.text(), self.inp_prenom.text(), self.inp_nationalite.text())
            self.refresh()
            QMessageBox.information(self, "Succès", "Auteur ajouté.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def on_delete(self):
        author_id = self.get_selected_id()
        if not author_id:
            return

        reply = QMessageBox.question(self, "Confirmation", "Supprimer cet auteur ?", QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return

        try:
            self.controller.delete_auteur(author_id)
            self.refresh()
            QMessageBox.information(self, "Succès", "Auteur supprimé.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

class ActionTablePage(BaseTablePage):
    def __init__(self, main_window, title, data_loader, columns, action_name=None, action_callback=None, require_admin=False):
        super().__init__(main_window, title)
        self.data_loader = data_loader
        self.set_columns(columns)
        self.action_callback = action_callback
        
        self.action_layout.addStretch()
        if action_name and action_callback:
            if not require_admin or self.is_admin:
                btn = QPushButton(action_name)
                btn.setObjectName("primaryAction")
                btn.clicked.connect(self.on_action)
                self.action_layout.addWidget(btn)

    def refresh(self):
        self.load_data(self.data_loader())

    def on_action(self):
        book_id = self.get_selected_id()
        if book_id: self.action_callback(book_id)

class MainWindow(QMainWindow):
    logout_requested = Signal()
    INITIAL_WIDTH = 1200
    INITIAL_HEIGHT = 750
    SCREEN_MARGIN = 80

    def __init__(self, current_user=None):
        super().__init__()
        self.setWindowTitle("Gestion de Bibliothèque - Premium Edition")
        self.set_initial_size()
        self.center_on_screen()
        
        self.current_user = current_user or {"username": "invite", "role": "user"}
        self.current_user["role"] = str(self.current_user.get("role", "user")).strip().lower()
        self.current_user["display_name"] = self.current_user.get("display_name") or self.current_user.get("username")
        self.is_admin = self.current_user["role"] == "admin"
        
        self.controller = LivreController()
        self.emprunt_controller = EmpruntController()
        self.auth_controller = AuthController()
        self.profile_controller = ProfileController()

        profile = self.profile_controller.get_profile(self.current_user.get("id_compte"))
        if profile and profile.get("nom"):
            self.current_user["display_name"] = profile["nom"]
        
        self.setup_ui()
        # Active le premier onglet au démarrage
        if getattr(self, "initial_widget", None) and getattr(self, "initial_button", None):
            self.switch_tab(self.initial_widget, self.initial_button)
        elif self.nav_buttons:
            first_widget = self.stacked_widget.widget(0)
            self.switch_tab(first_widget, self.nav_buttons[0])

    def set_initial_size(self):
        screen = self.screen() or QGuiApplication.primaryScreen()
        if not screen:
            self.resize(self.INITIAL_WIDTH, self.INITIAL_HEIGHT)
            return

        available = screen.availableGeometry()
        width = min(self.INITIAL_WIDTH, max(900, available.width() - self.SCREEN_MARGIN))
        height = min(self.INITIAL_HEIGHT, max(560, available.height() - self.SCREEN_MARGIN))
        self.resize(width, height)

    def center_on_screen(self):
        screen = self.screen() or QGuiApplication.primaryScreen()
        if not screen:
            return

        available = screen.availableGeometry()
        size = self.frameGeometry()
        x = available.x() + max(0, (available.width() - size.width()) // 2)
        y = available.y() + max(0, (available.height() - size.height()) // 2)
        self.move(x, y)

    def update_session_info_label(self, display_name=None):
        if display_name is None:
            display_name = self.current_user.get("display_name") or self.current_user["username"]
        else:
            self.current_user["display_name"] = display_name

        self.session_info_label.setText(f"{display_name} ({self.current_user['role']})")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(270)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 18, 14, 14)
        sidebar_layout.setSpacing(8)
        
        app_title = QLabel("BIBLIOTHÈQUE")
        app_title.setObjectName("sidebarTitle")
        app_title.setAlignment(Qt.AlignLeft)
        sidebar_layout.addWidget(app_title)

        display_name = self.current_user.get("display_name") or self.current_user["username"]
        self.session_info_label = QLabel(f"{display_name} ({self.current_user['role']})")
        self.session_info_label.setObjectName("sessionLabel")
        self.session_info_label.setAlignment(Qt.AlignLeft)
        sidebar_layout.addWidget(self.session_info_label)
        sidebar_layout.addSpacing(8)

        # Zone défilante pour les boutons de navigation
        nav_container = QWidget()
        nav_container.setObjectName("navContainer")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(6)
        nav_layout.setAlignment(Qt.AlignTop)
        
        nav_scroll = QScrollArea()
        nav_scroll.setObjectName("sidebarScroll")
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setWidget(nav_container)
        nav_scroll.setFrameShape(QFrame.NoFrame)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QWidget#navContainer { background: transparent; }
            QScrollBar:vertical { width: 4px; background: transparent; }
            QScrollBar::handle:vertical { background: #334155; border-radius: 2px; }
        """)
        # La scroll area prend tout l'espace disponible
        sidebar_layout.addWidget(nav_scroll, 1)

        self.nav_buttons = []
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("mainContainer")

        def add_nav(text, page_widget):
            self.stacked_widget.addWidget(page_widget)
            btn = QPushButton(text)
            btn.setProperty("class", "sidebarButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda _, w=page_widget, b=btn: self.switch_tab(w, b))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            return btn

        account_label = QLabel("Compte")
        account_label.setObjectName("sidebarSectionLabel")
        nav_layout.addWidget(account_label)
        add_nav("Mon Profil", ProfilePage(self, self.current_user))

        nav_layout.addSpacing(14)
        nav_label = QLabel("Navigation")
        nav_label.setObjectName("sidebarSectionLabel")
        nav_layout.addWidget(nav_label)

        dashboard_page = DashboardPage(self)
        self.initial_widget = dashboard_page
        self.initial_button = add_nav("Dashboard", dashboard_page)
        add_nav("Tous les livres", ManageBooksPage(self))
        add_nav("Livres les plus empruntés", ActionTablePage(
            self, "Livres les plus empruntés", self.emprunt_controller.get_livres_plus_empruntes,
            [("id_livre", "ID"), ("titre", "Titre"), ("auteur", "Auteur"), ("nombre_emprunts", "Nb emprunts")],
            "📤 Emprunter", self.borrow_callback
        ))
        add_nav("Auteurs", ManageAuthorsPage(self))
        
        add_nav("Emprunts", ActionTablePage(
            self, "Tous les emprunts" if self.is_admin else "Mes emprunts", 
            lambda: self.emprunt_controller.get_livres_empruntes() if self.is_admin else self.emprunt_controller.get_livres_empruntes_pour_compte(self.current_user),
            [("id_livre", "ID"), ("titre", "Titre"), ("auteur", "Auteur"), ("date_emprunt", "Emprunt"), ("date_limite", "Limite"), ("statut", "Statut")],
            "📥 Retourner", self.return_callback, require_admin=False if not self.is_admin else True
        ))
        add_nav("Retards", ActionTablePage(
            self, "Tous les retards" if self.is_admin else "Mes retards",
            lambda: self.emprunt_controller.get_livres_en_retard() if self.is_admin else self.emprunt_controller.get_livres_en_retard_pour_compte(self.current_user),
            [("id_livre", "ID"), ("titre", "Titre"), ("jours_retard", "Jours Retard"), ("statut", "Statut")],
            "📥 Retourner", self.return_callback, require_admin=False if not self.is_admin else True
        ))
        add_nav("Historique personnel", ActionTablePage(
            self, "Historique personnel", lambda: self.emprunt_controller.get_historique_emprunts_pour_compte(self.current_user),
            [("id_emprunt", "ID"), ("titre", "Titre"), ("date_emprunt", "Emprunt"), ("date_retour", "Retour")]
        ))
        
        if self.is_admin:
            add_nav("Mes emprunts admin", ActionTablePage(
                self, "Mes emprunts admin", lambda: self.emprunt_controller.get_livres_empruntes_pour_compte(self.current_user),
                [("id_livre", "ID"), ("titre", "Titre"), ("date_emprunt", "Emprunt"), ("date_limite", "Limite"), ("statut", "Statut")],
                "📥 Retourner", self.return_callback
            ))
            add_nav("Utilisateurs", ActionTablePage(
                self, "Utilisateurs", self.auth_controller.get_accounts,
                [("id_compte", "ID"), ("username", "Utilisateur"), ("role", "Rôle")],
                "Rendre Admin", self.make_admin_callback
            ))

        nav_layout.addSpacing(14)
        recommendation_label = QLabel("Recommendation")
        recommendation_label.setObjectName("sidebarSectionLabel")
        nav_layout.addWidget(recommendation_label)
        add_nav("Recommandations", RecommendationsPage(self))
        nav_layout.addStretch()

        btn_logout = QPushButton("Déconnexion")
        btn_logout.setObjectName("logoutButton")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setMinimumHeight(42)
        btn_logout.clicked.connect(self.logout)
        sidebar_layout.addWidget(btn_logout)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget, 1)

    def switch_tab(self, widget, btn):
        self.stacked_widget.setCurrentWidget(widget)
        for b in self.nav_buttons:
            b.setProperty("active", "false")
            b.style().unpolish(b)
            b.style().polish(b)
        btn.setProperty("active", "true")
        btn.style().unpolish(btn)
        btn.style().polish(btn)
        
        if hasattr(widget, "refresh"):
            widget.refresh()

    def borrow_callback(self, book_id):
        try:
            self.emprunt_controller.emprunter_livre_pour_compte(book_id, self.current_user)
            self.stacked_widget.currentWidget().refresh()
            QMessageBox.information(self, "Succès", "Livre emprunté.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def return_callback(self, book_id):
        try:
            self.emprunt_controller.retourner_livre_pour_compte(book_id, self.current_user)
            self.stacked_widget.currentWidget().refresh()
            QMessageBox.information(self, "Succès", "Livre retourné.")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", str(e))

    def make_admin_callback(self, user_id):
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous rendre cet utilisateur admin ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.auth_controller.make_admin(user_id)
                self.stacked_widget.currentWidget().refresh()
            except Exception as e:
                QMessageBox.warning(self, "Erreur", str(e))

    def logout(self):
        reply = QMessageBox.question(self, "Déconnexion", "Voulez-vous vous déconnecter ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()

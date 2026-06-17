class Emprunt:
    def __init__(self, id_emprunt, date_emprunt, date_retour, statut, id_livre, id_utilisateur, date_limite=""):
        self.id_emprunt = id_emprunt
        self.date_emprunt = date_emprunt
        self.date_limite = date_limite
        self.date_retour = date_retour
        self.statut = statut  # 'Actif' or 'Cloturé'
        self.id_livre = id_livre
        self.id_utilisateur = id_utilisateur

    def creer(self):
        self.statut = "Actif"

    def cloturer(self, date_retour):
        self.statut = "Cloturé"
        self.date_retour = date_retour

    def est_actif(self):
        return self.statut == "Actif"

    def to_dict(self):
        return {
            "id_emprunt": self.id_emprunt,
            "date_emprunt": self.date_emprunt,
            "date_limite": self.date_limite,
            "date_retour": self.date_retour,
            "statut": self.statut,
            "id_livre": self.id_livre,
            "id_utilisateur": self.id_utilisateur
        }

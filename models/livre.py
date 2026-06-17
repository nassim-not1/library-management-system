class Livre:
    def __init__(self, id_livre, titre, categorie, disponibilite, id_auteur, annee=""):
        self.id_livre = id_livre
        self.titre = titre
        self.categorie = categorie
        self.disponibilite = disponibilite  # 'Disponible' or 'Emprunté'
        self.id_auteur = id_auteur
        self.annee = annee

    def est_disponible(self):
        return self.disponibilite == "Disponible"

    def emprunter(self):
        self.disponibilite = "Emprunté"

    def retourner(self):
        self.disponibilite = "Disponible"

    def to_dict(self):
        return {
            "id_livre": self.id_livre,
            "titre": self.titre,
            "categorie": self.categorie,
            "disponibilite": self.disponibilite,
            "id_auteur": self.id_auteur,
            "annee": self.annee
        }

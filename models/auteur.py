class Auteur:
    def __init__(self, id_auteur, nom, prenom="", nationalite=""):
        self.id_auteur = id_auteur
        self.nom = nom
        self.prenom = prenom
        self.nationalite = nationalite

    def to_dict(self):
        return {
            "id_auteur": self.id_auteur,
            "nom": self.nom,
            "prenom": self.prenom,
            "nationalite": self.nationalite
        }

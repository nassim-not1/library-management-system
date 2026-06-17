class Utilisateur:
    def __init__(self, id_utilisateur, nom, prenom="", email=""):
        self.id_utilisateur = id_utilisateur
        self.nom = nom
        self.prenom = prenom
        self.email = email

    def to_dict(self):
        return {
            "id_utilisateur": self.id_utilisateur,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email
        }

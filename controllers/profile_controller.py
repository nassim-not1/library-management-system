import pandas as pd
from data.database import Database
from models.utilisateur import Utilisateur

class ProfileController:
    def __init__(self):
        self.db = Database()

    def get_profile(self, id_compte):
        """Récupère les informations du profil utilisateur lié au compte"""
        df = self.db.load_table("utilisateurs").fillna("")
        if df.empty:
            return None

        # Le lien se fait par id_utilisateur == id_compte
        mask = df["id_utilisateur"] == str(id_compte)
        if not mask.any():
            return None

        user_data = df[mask].iloc[0]
        return {
            "nom": str(user_data.get("nom", "")),
            "prenom": str(user_data.get("prenom", "")),
            "email": str(user_data.get("email", ""))
        }

    def update_profile(self, id_compte, nom, prenom, email, username=""):
        """Met à jour ou crée le profil s'il n'existe pas encore."""
        nom = str(nom).strip()
        prenom = str(prenom).strip()
        email = str(email).strip()

        df = self.db.load_table("utilisateurs").fillna("")
        
        # Si la table était complètement vide
        if df.empty:
            df = pd.DataFrame(columns=self.db.columns.get("utilisateurs", ["id_utilisateur", "nom", "prenom", "email"]))

        mask = df["id_utilisateur"] == str(id_compte)

        if not mask.any():
            # Le profil n'existe pas, on le crée (nom par défaut = username si nom vide)
            if not nom:
                nom = str(username)
            new_user = Utilisateur(str(id_compte), nom, prenom, email)
            new_row = pd.DataFrame([new_user.to_dict()])
            df = pd.concat([df, new_row], ignore_index=True)
        else:
            # On met à jour
            if not nom: # Eviter d'effacer totalement le nom
                nom = str(df.loc[mask, "nom"].iloc[0])
            df.loc[mask, "nom"] = nom
            df.loc[mask, "prenom"] = prenom
            df.loc[mask, "email"] = email

        self.db.save_table("utilisateurs", df)

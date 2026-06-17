import pandas as pd
from models.livre import Livre
from models.auteur import Auteur
from data.database import Database

class LivreController:
    def __init__(self):
        self.db = Database()

    def _format_auteur(self, row):
        nom = str(row.get("nom", "")).strip()
        prenom = str(row.get("prenom", "")).strip()
        return f"{nom} {prenom}".strip()

    def get_all_auteurs(self):
        df_auteurs = self.db.load_table("auteurs").fillna("")
        if df_auteurs.empty:
            return []

        df_auteurs["auteur"] = df_auteurs.apply(self._format_auteur, axis=1)
        df_auteurs = df_auteurs.sort_values(by=["nom", "prenom"], kind="stable")
        return df_auteurs.to_dict("records")

    def add_auteur(self, nom, prenom="", nationalite=""):
        nom = str(nom).strip()
        prenom = str(prenom).strip()
        nationalite = str(nationalite).strip()

        if not nom:
            raise ValueError("Le nom de l'auteur est obligatoire.")

        df_auteurs = self.db.load_table("auteurs").fillna("")
        if not df_auteurs.empty:
            mask = (
                (df_auteurs["nom"].str.lower() == nom.lower()) &
                (df_auteurs["prenom"].str.lower() == prenom.lower())
            )
            if mask.any():
                raise ValueError("Cet auteur existe deja.")

        new_id = self.db.generate_id("auteurs", "id_auteur")
        nouvel_auteur = Auteur(new_id, nom, prenom, nationalite)
        new_row = pd.DataFrame([nouvel_auteur.to_dict()])
        df_auteurs = pd.concat([df_auteurs, new_row], ignore_index=True)
        self.db.save_table("auteurs", df_auteurs)

    def _resolve_auteur_id(self, auteur_ref):
        auteur_ref = str(auteur_ref).strip()
        df_auteurs = self.db.load_table("auteurs").fillna("")

        if not auteur_ref:
            raise ValueError("L'auteur est obligatoire.")
        if df_auteurs.empty:
            raise ValueError("Aucun auteur disponible. Ajoutez d'abord un auteur.")

        id_mask = df_auteurs["id_auteur"] == auteur_ref
        if id_mask.any():
            return auteur_ref

        df_auteurs["auteur"] = df_auteurs.apply(self._format_auteur, axis=1)
        name_mask = df_auteurs["auteur"].str.lower() == auteur_ref.lower()
        if name_mask.any():
            return str(df_auteurs[name_mask].iloc[0]["id_auteur"])

        raise ValueError("Auteur introuvable. Ajoutez d'abord l'auteur dans la section Auteurs.")

    def get_all_livres(self):
        df_livres = self.db.load_table("livres")
        df_auteurs = self.db.load_table("auteurs")
        
        if df_livres.empty:
            return []
            
        # Merge to get author name
        if not df_auteurs.empty:
            df_merged = pd.merge(df_livres, df_auteurs, on="id_auteur", how="left")
            df_merged["auteur"] = df_merged["nom"].fillna("") + " " + df_merged["prenom"].fillna("")
            df_merged["auteur"] = df_merged["auteur"].str.strip()
            df_merged["statut"] = df_merged["disponibilite"] # Map for UI compat
        else:
            df_merged = df_livres.copy()
            df_merged["auteur"] = "Inconnu"
            df_merged["statut"] = df_merged["disponibilite"]
            
        return df_merged.fillna("").to_dict('records')

    def add_livre(self, titre, auteur_ref, categorie, annee):
        if not titre or not auteur_ref:
            raise ValueError("Le titre et l'auteur sont obligatoires.")
        
        id_auteur = self._resolve_auteur_id(auteur_ref)
        
        df = self.db.load_table("livres")
        new_id = self.db.generate_id("livres", "id_livre")
        nouveau_livre = Livre(new_id, titre, categorie, "Disponible", id_auteur, annee)
        
        new_row = pd.DataFrame([nouveau_livre.to_dict()])
        df = pd.concat([df, new_row], ignore_index=True)
        self.db.save_table("livres", df)

    def update_livre(self, id_livre, titre, auteur_ref, categorie, annee):
        if not titre or not auteur_ref:
            raise ValueError("Le titre et l'auteur sont obligatoires.")

        id_auteur = self._resolve_auteur_id(auteur_ref)

        df = self.db.load_table("livres")
        mask = df["id_livre"] == str(id_livre)
        if not mask.any():
            raise ValueError("Livre introuvable.")
        
        df.loc[mask, "titre"] = titre
        df.loc[mask, "id_auteur"] = id_auteur
        df.loc[mask, "categorie"] = categorie
        df.loc[mask, "annee"] = annee
        self.db.save_table("livres", df)

    def delete_livre(self, id_livre):
        df = self.db.load_table("livres")
        mask = df["id_livre"] == str(id_livre)
        if not mask.any():
            raise ValueError("Livre introuvable.")
        
        # Vérification sécurisée : empêcher la suppression si le livre est emprunté
        livre = df[mask].iloc[0]
        disponibilite = str(livre.get("disponibilite", "")).strip().lower()
        if disponibilite in ("emprunté", "emprunte", "borrowed"):
            titre = str(livre.get("titre", f"ID {id_livre}"))
            raise ValueError(
                f"Impossible de supprimer « {titre} » : ce livre est actuellement emprunté.\n"
                "Veuillez attendre son retour avant de le supprimer."
            )
        
        df = df[~mask]
        self.db.save_table("livres", df)

    def search_livres(self, keyword):
        livres = self.get_all_livres()
        if not livres:
            return []
            
        keyword = str(keyword).lower()
        result = []
        for l in livres:
            if (keyword in str(l.get('titre', '')).lower() or 
                keyword in str(l.get('auteur', '')).lower() or 
                keyword in str(l.get('categorie', '')).lower()):
                result.append(l)
        return result

    def get_livres_empruntes(self):
        livres = self.get_all_livres()
        return [l for l in livres if l.get('disponibilite') == "Emprunté"]

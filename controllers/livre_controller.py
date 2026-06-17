import re
import unicodedata

import pandas as pd
from models.livre import Livre
from models.auteur import Auteur
from data.database import Database
from services.recommendation_service import RecommendationService

class LivreController:
    def __init__(self):
        self.db = Database()
        self.recommendation_service = RecommendationService()

    def _format_auteur(self, row):
        nom = str(row.get("nom", "")).strip()
        prenom = str(row.get("prenom", "")).strip()
        return f"{nom} {prenom}".strip()

    def _normalize_text(self, value):
        value = str(value).strip().casefold()
        value = unicodedata.normalize("NFKD", value)
        value = "".join(char for char in value if not unicodedata.combining(char))
        value = re.sub(r"[^a-z0-9]+", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    def _ensure_livre_unique(self, df_livres, titre, id_auteur, exclude_id=None):
        if df_livres.empty:
            return

        titre_normalise = self._normalize_text(titre)
        id_auteur = str(id_auteur).strip()
        mask = (
            df_livres["titre"].fillna("").apply(self._normalize_text).eq(titre_normalise) &
            df_livres["id_auteur"].fillna("").astype(str).str.strip().eq(id_auteur)
        )

        if exclude_id is not None:
            mask = mask & ~df_livres["id_livre"].astype(str).eq(str(exclude_id))

        if mask.any():
            raise ValueError("Ce livre existe deja pour cet auteur.")

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

    def delete_auteur(self, id_auteur):
        df_auteurs = self.db.load_table("auteurs").fillna("")
        mask = df_auteurs["id_auteur"] == str(id_auteur)
        if not mask.any():
            raise ValueError("Auteur introuvable.")

        df_livres = self.db.load_table("livres").fillna("")
        if not df_livres.empty and (df_livres["id_auteur"] == str(id_auteur)).any():
            auteur = df_auteurs[mask].iloc[0]
            nom_complet = self._format_auteur(auteur) or f"ID {id_auteur}"
            raise ValueError(
                f"Impossible de supprimer {nom_complet} : des livres sont encore associes a cet auteur."
            )

        df_auteurs = df_auteurs[~mask]
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

    def add_livre(self, titre, auteur_ref, categorie, annee, description="", mots_cles=""):
        if not titre or not auteur_ref:
            raise ValueError("Le titre et l'auteur sont obligatoires.")
        
        id_auteur = self._resolve_auteur_id(auteur_ref)
        
        df = self.db.load_table("livres")
        self._ensure_livre_unique(df, titre, id_auteur)
        new_id = self.db.generate_id("livres", "id_livre")
        nouveau_livre = Livre(new_id, titre, categorie, "Disponible", id_auteur, annee, description, mots_cles)
        
        new_row = pd.DataFrame([nouveau_livre.to_dict()])
        df = pd.concat([df, new_row], ignore_index=True)
        self.db.save_table("livres", df)

    def update_livre(self, id_livre, titre, auteur_ref, categorie, annee, description="", mots_cles=""):
        if not titre or not auteur_ref:
            raise ValueError("Le titre et l'auteur sont obligatoires.")

        id_auteur = self._resolve_auteur_id(auteur_ref)

        df = self.db.load_table("livres")
        mask = df["id_livre"] == str(id_livre)
        if not mask.any():
            raise ValueError("Livre introuvable.")

        self._ensure_livre_unique(df, titre, id_auteur, exclude_id=id_livre)
        
        df.loc[mask, "titre"] = titre
        df.loc[mask, "id_auteur"] = id_auteur
        df.loc[mask, "categorie"] = categorie
        df.loc[mask, "annee"] = annee
        df.loc[mask, "description"] = description
        df.loc[mask, "mots_cles"] = mots_cles
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

    def get_livres_recommandes(self, id_livre, top_n=5):
        livres = self.get_all_livres()
        return self.recommendation_service.recommend_by_book(livres, id_livre, top_n)

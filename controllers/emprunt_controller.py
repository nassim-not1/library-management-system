import pandas as pd
from datetime import datetime, timedelta
from models.emprunt import Emprunt
from models.utilisateur import Utilisateur
from data.database import Database

class EmpruntController:
    DUREE_EMPRUNT_JOURS = 14

    def __init__(self):
        self.db = Database()

    def _parse_date(self, value):
        value = str(value).strip()
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _calculer_date_limite(self, date_emprunt):
        parsed_date = self._parse_date(date_emprunt)
        if not parsed_date:
            parsed_date = datetime.now().date()

        return (parsed_date + timedelta(days=self.DUREE_EMPRUNT_JOURS)).strftime("%Y-%m-%d")

    def _ajouter_dates_limites_manquantes(self, df_emprunts):
        df_emprunts = df_emprunts.copy()
        if "date_limite" not in df_emprunts.columns:
            df_emprunts["date_limite"] = ""

        date_limite_vide = df_emprunts["date_limite"].fillna("").astype(str).str.strip() == ""
        df_emprunts.loc[date_limite_vide, "date_limite"] = df_emprunts.loc[
            date_limite_vide,
            "date_emprunt",
        ].apply(self._calculer_date_limite)
        return df_emprunts
    
    def _find_utilisateur_id(self, nom, prenom="", email=""):
        df = self.db.load_table("utilisateurs").fillna("")
        if df.empty:
            return None

        nom = str(nom).strip()
        prenom = str(prenom).strip()
        email = str(email).strip()

        if email:
            mask = df["email"].str.lower() == email.lower()
        else:
            mask = (df["nom"].str.lower() == nom.lower()) & (df["prenom"].str.lower() == prenom.lower())

        if mask.any():
            return str(df[mask].iloc[0]["id_utilisateur"])

        return None

    def _get_or_create_utilisateur(self, nom, prenom, email):
        existing_id = self._find_utilisateur_id(nom, prenom, email)
        if existing_id:
            return existing_id

        df = self.db.load_table("utilisateurs").fillna("")
        
        # Create new
        new_id = self.db.generate_id("utilisateurs", "id_utilisateur")
        nouvel_utilisateur = Utilisateur(new_id, nom, prenom, email)
        
        new_row = pd.DataFrame([nouvel_utilisateur.to_dict()])
        df = pd.concat([df, new_row], ignore_index=True)
        self.db.save_table("utilisateurs", df)
        return new_id

    def _get_utilisateur_id_pour_compte(self, compte):
        id_compte = str(compte.get("id_compte", "")).strip()
        if not id_compte:
            return None

        # S'assurer que le profil existe dans "utilisateurs" pour cet id_compte
        df = self.db.load_table("utilisateurs").fillna("")
        if df.empty or not (df["id_utilisateur"] == id_compte).any():
            username = str(compte.get("username", ""))
            new_row = pd.DataFrame([{
                "id_utilisateur": id_compte,
                "nom": username,
                "prenom": "",
                "email": ""
            }])
            df = pd.concat([df, new_row], ignore_index=True) if not df.empty else new_row
            self.db.save_table("utilisateurs", df)

        return id_compte

    def emprunter_livre_pour_compte(self, id_livre, compte):
        id_utilisateur = self._get_utilisateur_id_pour_compte(compte)
        if not id_utilisateur:
            raise ValueError("Aucun utilisateur connecte.")

        self._emprunter_livre_pour_utilisateur_id(id_livre, id_utilisateur)

    def get_livres_empruntes(self):
        return self._get_livres_empruntes_actifs()

    def get_livres_empruntes_pour_compte(self, compte):
        id_utilisateur = self._get_utilisateur_id_pour_compte(compte)
        if not id_utilisateur:
            return []

        return self._get_livres_empruntes_actifs(id_utilisateur)

    def get_livres_en_retard(self):
        return self._get_livres_en_retard_actifs()

    def get_livres_en_retard_pour_compte(self, compte):
        id_utilisateur = self._get_utilisateur_id_pour_compte(compte)
        if not id_utilisateur:
            return []

        return self._get_livres_en_retard_actifs(id_utilisateur)

    def get_historique_emprunts_pour_compte(self, compte):
        id_utilisateur = self._get_utilisateur_id_pour_compte(compte)
        if not id_utilisateur:
            return []

        return self._get_historique_emprunts(id_utilisateur)

    
    def _get_livres_en_retard_actifs(self, id_utilisateur=None):
        livres = self._get_livres_empruntes_actifs(id_utilisateur)
        today = datetime.now().date()
        livres_en_retard = []

        for livre in livres:
            date_limite = self._parse_date(livre.get("date_limite", ""))
            if not date_limite:
                continue

            jours_retard = (today - date_limite).days
            if jours_retard > 0:
                livre = livre.copy()
                livre["jours_retard"] = str(jours_retard)
                livre["statut"] = "En retard"
                livres_en_retard.append(livre)

        return livres_en_retard

    def get_livres_plus_empruntes(self):
        df_emprunts = self.db.load_table("emprunts").fillna("")
        if df_emprunts.empty:
            return []

        df_livres = self.db.load_table("livres").fillna("")
        if df_livres.empty:
            return []

        counts = (
            df_emprunts.groupby("id_livre")
            .size()
            .reset_index(name="nombre_emprunts")
        )

        df_merged = pd.merge(counts, df_livres, on="id_livre", how="inner")
        if df_merged.empty:
            return []

        df_auteurs = self.db.load_table("auteurs").fillna("")
        if not df_auteurs.empty:
            df_merged = pd.merge(df_merged, df_auteurs, on="id_auteur", how="left")
            df_merged["auteur"] = df_merged["nom"].fillna("") + " " + df_merged["prenom"].fillna("")
            df_merged["auteur"] = df_merged["auteur"].str.strip()
        else:
            df_merged["auteur"] = "Inconnu"

        df_merged["statut"] = df_merged["disponibilite"]
        df_merged = df_merged.sort_values(
            by=["nombre_emprunts", "titre"],
            ascending=[False, True],
        )
        return df_merged.fillna("").to_dict("records")

    def _get_livres_empruntes_actifs(self, id_utilisateur=None):
        df_emprunts = self.db.load_table("emprunts").fillna("")
        if df_emprunts.empty:
            return []

        df_emprunts = self._ajouter_dates_limites_manquantes(df_emprunts)

        mask = df_emprunts["statut"] == "Actif"
        if id_utilisateur is not None:
            mask = mask & (df_emprunts["id_utilisateur"] == str(id_utilisateur))

        df_emprunts = df_emprunts[mask]
        if df_emprunts.empty:
            return []

        df_livres = self.db.load_table("livres").fillna("")
        if df_livres.empty:
            return []

        df_merged = pd.merge(df_emprunts, df_livres, on="id_livre", how="inner")
        if df_merged.empty:
            return []

        df_utilisateurs = self.db.load_table("utilisateurs").fillna("")
        if not df_utilisateurs.empty:
            df_utilisateurs = df_utilisateurs.rename(columns={
                "nom": "nom_utilisateur",
                "prenom": "prenom_utilisateur",
                "email": "email_utilisateur",
            })
            df_merged = pd.merge(df_merged, df_utilisateurs, on="id_utilisateur", how="left")
        else:
            df_merged["nom_utilisateur"] = ""
            df_merged["prenom_utilisateur"] = ""
            df_merged["email_utilisateur"] = ""

        df_auteurs = self.db.load_table("auteurs").fillna("")
        if not df_auteurs.empty:
            df_merged = pd.merge(df_merged, df_auteurs, on="id_auteur", how="left")
            df_merged["auteur"] = df_merged["nom"].fillna("") + " " + df_merged["prenom"].fillna("")
            df_merged["auteur"] = df_merged["auteur"].str.strip()
        else:
            df_merged["auteur"] = "Inconnu"

        df_merged["statut"] = "Emprunté"
        df_merged["emprunteur"] = (
            df_merged["nom_utilisateur"].fillna("") + " " + df_merged["prenom_utilisateur"].fillna("")
        ).str.strip()
        df_merged.loc[df_merged["emprunteur"] == "", "emprunteur"] = (
            "Utilisateur " + df_merged["id_utilisateur"].astype(str)
        )
        return df_merged.fillna("").to_dict("records")

    def _get_historique_emprunts(self, id_utilisateur):
        df_emprunts = self.db.load_table("emprunts").fillna("")
        if df_emprunts.empty:
            return []

        df_emprunts = self._ajouter_dates_limites_manquantes(df_emprunts)
        df_emprunts = df_emprunts[df_emprunts["id_utilisateur"] == str(id_utilisateur)]
        if df_emprunts.empty:
            return []

        df_livres = self.db.load_table("livres").fillna("")
        if df_livres.empty:
            return []

        df_merged = pd.merge(df_emprunts, df_livres, on="id_livre", how="inner")
        if df_merged.empty:
            return []

        df_auteurs = self.db.load_table("auteurs").fillna("")
        if not df_auteurs.empty:
            df_merged = pd.merge(df_merged, df_auteurs, on="id_auteur", how="left")
            df_merged["auteur"] = df_merged["nom"].fillna("") + " " + df_merged["prenom"].fillna("")
            df_merged["auteur"] = df_merged["auteur"].str.strip()
        else:
            df_merged["auteur"] = "Inconnu"

        today = datetime.now().date()

        def statut_historique(row):
            if str(row.get("statut", "")) == "Actif":
                date_limite = self._parse_date(row.get("date_limite", ""))
                if date_limite and (today - date_limite).days > 0:
                    return "En retard"
                return "Emprunte"
            return "Retourne"

        df_merged["statut"] = df_merged.apply(statut_historique, axis=1)
        df_merged["_date_tri"] = pd.to_datetime(df_merged["date_emprunt"], errors="coerce")
        df_merged["_id_tri"] = pd.to_numeric(df_merged["id_emprunt"], errors="coerce").fillna(0)
        df_merged = df_merged.sort_values(by=["_date_tri", "_id_tri"], ascending=[False, False])
        df_merged = df_merged.drop(columns=["_date_tri", "_id_tri"])
        return df_merged.fillna("").to_dict("records")

    def _emprunter_livre_pour_utilisateur_id(self, id_livre, id_user):
        df_livres = self.db.load_table("livres")
        mask_livre = df_livres["id_livre"] == str(id_livre)
        if not mask_livre.any():
            raise ValueError("Livre introuvable.")

        disponibilite = str(df_livres.loc[mask_livre, "disponibilite"].values[0]).strip().lower()
        if "emprunt" in disponibilite:
            raise ValueError("Ce livre est deja emprunte.")

        df_emprunts = self.db.load_table("emprunts")
        new_id = self.db.generate_id("emprunts", "id_emprunt")
        date_emprunt = datetime.now().strftime("%Y-%m-%d")
        date_limite = (datetime.now() + timedelta(days=self.DUREE_EMPRUNT_JOURS)).strftime("%Y-%m-%d")

        nouvel_emprunt = Emprunt(new_id, date_emprunt, "", "Actif", id_livre, id_user, date_limite)
        new_row = pd.DataFrame([nouvel_emprunt.to_dict()])
        df_emprunts = pd.concat([df_emprunts, new_row], ignore_index=True)
        self.db.save_table("emprunts", df_emprunts)

        df_livres.loc[mask_livre, "disponibilite"] = "Emprunte"
        self.db.save_table("livres", df_livres)

    
    def emprunter_livre(self, id_livre, nom_utilisateur, prenom_utilisateur, email=""):
        # Verifier livre dispo
        df_livres = self.db.load_table("livres")
        mask_livre = df_livres["id_livre"] == str(id_livre)
        if not mask_livre.any():
            raise ValueError("Livre introuvable.")

        
            
        if df_livres.loc[mask_livre, "disponibilite"].values[0] == "Emprunté":
            raise ValueError("Ce livre est déjà emprunté.")
            
        id_user = self._get_or_create_utilisateur(nom_utilisateur, prenom_utilisateur, email)
        
        # Creer l'emprunt
        df_emprunts = self.db.load_table("emprunts")
        new_id = self.db.generate_id("emprunts", "id_emprunt")
        date_emprunt = datetime.now().strftime("%Y-%m-%d")
        date_limite = (datetime.now() + timedelta(days=self.DUREE_EMPRUNT_JOURS)).strftime("%Y-%m-%d")
        
        nouvel_emprunt = Emprunt(new_id, date_emprunt, "", "Actif", id_livre, id_user, date_limite)
        new_row = pd.DataFrame([nouvel_emprunt.to_dict()])
        df_emprunts = pd.concat([df_emprunts, new_row], ignore_index=True)
        self.db.save_table("emprunts", df_emprunts)
        
        # Mettre à jour la dispo du livre
        df_livres.loc[mask_livre, "disponibilite"] = "Emprunté"
        self.db.save_table("livres", df_livres)

    def retourner_livre_pour_compte(self, id_livre, compte):
        id_utilisateur = self._get_utilisateur_id_pour_compte(compte)
        if not id_utilisateur:
            raise ValueError("Ce livre n'est pas emprunte par votre compte.")

        self.retourner_livre(id_livre, id_utilisateur)

    def retourner_livre(self, id_livre, id_utilisateur=None):
        df_livres = self.db.load_table("livres")
        mask_livre = df_livres["id_livre"] == str(id_livre)
        if not mask_livre.any():
            raise ValueError("Livre introuvable.")
            
        # Mettre a jour emprunt
        df_emprunts = self.db.load_table("emprunts").fillna("")
        mask_emprunt = (df_emprunts["id_livre"] == str(id_livre)) & (df_emprunts["statut"] == "Actif")
        if id_utilisateur is not None:
            mask_emprunt = mask_emprunt & (df_emprunts["id_utilisateur"] == str(id_utilisateur))

        if not mask_emprunt.any():
            if id_utilisateur is None:
                raise ValueError("Ce livre est déjà disponible.")
            raise ValueError("Ce livre n'est pas emprunte par votre compte.")

        df_emprunts.loc[mask_emprunt, "statut"] = "Cloturé"
        df_emprunts.loc[mask_emprunt, "date_retour"] = datetime.now().strftime("%Y-%m-%d")
        self.db.save_table("emprunts", df_emprunts)
            
        # Mettre à jour la dispo du livre
        df_livres.loc[mask_livre, "disponibilite"] = "Disponible"
        self.db.save_table("livres", df_livres)

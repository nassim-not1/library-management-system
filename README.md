# Gestion de Bibliotheque

Application desktop de gestion de bibliotheque developpee en Python avec PySide6 et MySQL.

Elle permet de gerer les livres, les auteurs, les emprunts, les retards, les comptes utilisateurs et les recommandations de livres basees sur TF-IDF et la similarite cosinus.

## Fonctionnalites

- Authentification avec comptes `admin` et `user`.
- Creation de compte utilisateur.
- Tableau de bord avec statistiques principales.
- Gestion des livres :
  - ajout, modification et suppression ;
  - champs `description` et `mots_cles` ;
  - prevention des doublons pour un meme livre et un meme auteur.
- Gestion des auteurs.
- Emprunt et retour de livres.
- Suivi des emprunts actifs.
- Detection des retards.
- Historique personnel des emprunts.
- Gestion des utilisateurs par l'administrateur.
- Profil utilisateur et changement de mot de passe.
- Recommandations de livres par contenu :
  - choix d'un livre ;
  - calcul TF-IDF ;
  - similarite cosinus ;
  - affichage des livres les plus proches.

## Technologies

- Python
- PySide6
- pandas
- MySQL
- mysql-connector-python
- scikit-learn

## Installation

1. Cloner ou ouvrir le dossier du projet.

2. Creer un environnement virtuel :

```powershell
python -m venv .venv
```

3. Activer l'environnement virtuel :

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Installer les dependances :

```powershell
pip install -r requirements.txt
```

## Configuration MySQL

L'application utilise MySQL. Le serveur MySQL doit etre lance avant de demarrer l'application.

Configuration par defaut :

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=gestion_bibliotheque
MYSQL_USER=root
MYSQL_PASSWORD=
```

Si votre configuration MySQL est differente, definissez les variables d'environnement avant le lancement.

Exemple PowerShell :

```powershell
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_DATABASE="gestion_bibliotheque"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="votre_mot_de_passe"
```

Au premier lancement, l'application cree automatiquement :

- la base de donnees si elle n'existe pas ;
- les tables necessaires ;
- les colonnes manquantes ;
- les donnees initiales depuis les fichiers CSV si les tables sont vides.

## Lancement

```powershell
python main.py
```

## Comptes par defaut

| Role | Nom d'utilisateur | Mot de passe |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Utilisateur | `user` | `user123` |

## Donnees initiales

Les donnees de depart sont dans le dossier `data` :

- `livres.csv`
- `auteurs.csv`
- `emprunts.csv`
- `utilisateurs.csv`
- `comptes.csv`

Important : les CSV sont migres une seule fois vers MySQL, lors de la premiere initialisation. Si la base MySQL contient deja des donnees, modifier les CSV ne mettra pas automatiquement a jour la base existante.

## Structure du projet

```text
gestion_bibliotheque/
  main.py
  requirements.txt
  mysql_config_example.txt
  controllers/
    auth_controller.py
    emprunt_controller.py
    livre_controller.py
    profile_controller.py
  data/
    database.py
    auteurs.csv
    livres.csv
    emprunts.csv
    utilisateurs.csv
    comptes.csv
  models/
    auteur.py
    emprunt.py
    livre.py
    utilisateur.py
  services/
    recommendation_service.py
  views/
    login_dialog.py
    main_window.py
    profile_page.py
    register_dialog.py
    style.py
```

## Recommandations

Le systeme de recommandation compare les livres a partir de ces champs :

- titre ;
- auteur ;
- categorie ;
- description ;
- mots cles.

Dans l'application :

1. Ouvrir la section `Recommandations`.
2. Choisir un livre.
3. Cliquer sur `Recommander`.
4. Consulter les livres similaires affiches dans le tableau.

## Remarques

- Le style de l'application est defini dans `views/style.py`.

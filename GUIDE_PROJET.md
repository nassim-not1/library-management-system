# Guide complet pour comprendre le projet

Ce fichier explique le projet de maniere simple et structuree. L'objectif est de comprendre comment l'application fonctionne, quels fichiers sont importants, comment les donnees circulent, et ou modifier le code quand on veut ajouter une fonctionnalite.

## 1. Idee generale du projet

Le projet est une application desktop de gestion de bibliotheque.

Elle permet de :

- se connecter avec un compte ;
- creer un compte ;
- consulter un tableau de bord ;
- gerer les livres ;
- gerer les auteurs ;
- emprunter et retourner des livres ;
- detecter les retards ;
- consulter un historique personnel ;
- gerer les utilisateurs pour l'admin ;
- modifier son profil ;
- recommander des livres similaires avec TF-IDF et cosine similarity.

L'application est developpee avec :

| Technologie | Role |
| --- | --- |
| Python | Langage principal |
| PySide6 | Interface graphique desktop |
| MySQL | Base de donnees |
| pandas | Manipulation des tables sous forme de DataFrame |
| mysql-connector-python | Connexion entre Python et MySQL |
| scikit-learn | TF-IDF et cosine similarity pour les recommandations |

## 2. Vue rapide de l'architecture

Le projet suit une organisation proche du modele MVC :

```text
Utilisateur
  |
  v
Views PySide6
  |
  v
Controllers
  |
  v
Database / Services / Models
  |
  v
MySQL
```

Les vues affichent l'interface. Les controllers appliquent les regles metier. La classe `Database` lit et ecrit les donnees. Les models servent a construire des objets propres avant sauvegarde. Le service de recommandation contient la logique TF-IDF.

## 3. Structure des dossiers

```text
gestion_bibliotheque/
  main.py
  requirements.txt
  README.md
  GUIDE_PROJET.md
  controllers/
  data/
  models/
  services/
  views/
```

### `main.py`

C'est le point de depart du programme.

Son role :

1. creer l'application PySide6 ;
2. appliquer le style global ;
3. afficher la fenetre de connexion ;
4. ouvrir la fenetre principale apres connexion ;
5. revenir a la connexion apres deconnexion ;
6. quitter si l'utilisateur ferme la fenetre principale.

### `controllers/`

Ce dossier contient la logique metier.

| Fichier | Role |
| --- | --- |
| `auth_controller.py` | Connexion, creation de compte, roles, mot de passe |
| `livre_controller.py` | Livres, auteurs, doublons, recommandations |
| `emprunt_controller.py` | Emprunts, retours, retards, historique |
| `profile_controller.py` | Profil utilisateur |

### `data/`

Ce dossier contient la base de donnees et les donnees initiales.

| Fichier | Role |
| --- | --- |
| `database.py` | Connexion MySQL, creation tables, lecture/ecriture |
| `livres.csv` | Donnees initiales des livres |
| `auteurs.csv` | Donnees initiales des auteurs |
| `emprunts.csv` | Donnees initiales des emprunts |
| `utilisateurs.csv` | Donnees initiales des profils |
| `comptes.csv` | Donnees initiales des comptes |

Les CSV servent surtout a initialiser la base MySQL au premier lancement.

### `models/`

Ce dossier contient les classes simples qui representent les donnees principales.

| Model | Fichier | Table associee |
| --- | --- | --- |
| `Livre` | `models/livre.py` | `livres` |
| `Auteur` | `models/auteur.py` | `auteurs` |
| `Emprunt` | `models/emprunt.py` | `emprunts` |
| `Utilisateur` | `models/utilisateur.py` | `utilisateurs` |

Chaque model contient une methode `to_dict()` pour transformer l'objet en dictionnaire avant sauvegarde.

### `services/`

Ce dossier contient la logique specialisee.

| Fichier | Role |
| --- | --- |
| `recommendation_service.py` | Recommandation de livres avec TF-IDF et cosine similarity |

### `views/`

Ce dossier contient l'interface graphique.

| Fichier | Role |
| --- | --- |
| `login_dialog.py` | Fenetre de connexion |
| `register_dialog.py` | Fenetre de creation de compte |
| `main_window.py` | Fenetre principale, sidebar, pages |
| `profile_page.py` | Page de profil utilisateur |
| `style.py` | Style QSS de l'application |

## 4. Flux de demarrage

Le lancement commence dans `main.py`.

Flux :

1. `QApplication` est cree.
2. Le theme `LIGHT_THEME_QSS` est applique.
3. `LoginDialog` est affiche.
4. Si la connexion echoue, l'utilisateur reste sur la fenetre de connexion.
5. Si la connexion reussit, `MainWindow` est creee avec l'utilisateur connecte.
6. Si l'utilisateur clique sur deconnexion, on revient a `LoginDialog`.
7. Si l'utilisateur ferme la fenetre avec le bouton de fermeture, l'application se termine.

## 5. Base de donnees

La classe centrale est `Database` dans `data/database.py`.

Quand un controller cree une instance de `Database`, cette classe :

1. lit la configuration MySQL ;
2. verifie que `mysql-connector-python` est disponible ;
3. cree la base si elle n'existe pas ;
4. cree les tables ;
5. ajoute les colonnes manquantes si besoin ;
6. migre les CSV vers MySQL une seule fois.

### Tables principales

| Table | Description |
| --- | --- |
| `comptes` | Authentification et roles |
| `utilisateurs` | Informations personnelles du profil |
| `auteurs` | Auteurs des livres |
| `livres` | Catalogue |
| `emprunts` | Emprunts actifs et historiques |
| `app_metadata` | Informations internes comme migration CSV |

### Colonnes importantes

`comptes` :

- `id_compte`
- `username`
- `password_salt`
- `password_hash`
- `role`

`livres` :

- `id_livre`
- `titre`
- `categorie`
- `disponibilite`
- `id_auteur`
- `annee`
- `description`
- `mots_cles`

`emprunts` :

- `id_emprunt`
- `date_emprunt`
- `date_limite`
- `date_retour`
- `statut`
- `id_livre`
- `id_utilisateur`

## 6. Relations entre les donnees

Les relations sont logiques dans le code.

| Relation | Explication |
| --- | --- |
| `auteurs.id_auteur` vers `livres.id_auteur` | Un auteur peut avoir plusieurs livres |
| `livres.id_livre` vers `emprunts.id_livre` | Un livre peut avoir plusieurs emprunts dans l'historique |
| `utilisateurs.id_utilisateur` vers `emprunts.id_utilisateur` | Un utilisateur peut effectuer plusieurs emprunts |
| `comptes.id_compte` vers `utilisateurs.id_utilisateur` | Le profil du compte utilise le meme identifiant |

Important : le SQL actuel ne declare pas explicitement des contraintes `FOREIGN KEY`. Les liens sont geres par le code.

## 7. Authentification

Fichiers concernes :

- `views/login_dialog.py`
- `views/register_dialog.py`
- `controllers/auth_controller.py`

### Connexion

Flux :

1. L'utilisateur saisit username et password.
2. `LoginDialog.login()` appelle `AuthController.authenticate()`.
3. Le controller charge la table `comptes`.
4. Il cherche le username.
5. Il recalcule le hash du mot de passe avec le salt.
6. Il compare le hash calcule avec le hash stocke.
7. Si c'est correct, il retourne un dictionnaire utilisateur.
8. Sinon, la page affiche un message d'erreur et reste ouverte.

### Creation de compte

Flux :

1. L'utilisateur ouvre `RegisterDialog`.
2. Il saisit username, password et confirmation.
3. La confirmation doit etre identique au password.
4. `AuthController.create_account()` verifie que le username n'existe pas deja.
5. Un salt et un hash sont generes.
6. Le compte est sauvegarde avec le role `user`.

### Comptes par defaut

Si la table `comptes` est vide, le controller cree :

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| User | `user` | `user123` |

## 8. Fenetre principale

Fichier : `views/main_window.py`.

La classe principale est `MainWindow`.

Elle cree :

- la sidebar ;
- le nom de session ;
- les boutons de navigation ;
- le conteneur de pages `QStackedWidget` ;
- les controllers principaux ;
- les callbacks globaux.

Quand un bouton de navigation est clique :

1. `switch_tab(widget, btn)` est appelee.
2. Le `QStackedWidget` affiche la page demandee.
3. Le bouton actif change de style.
4. La page appelle `refresh()` si elle possede cette methode.

## 9. Pages de la sidebar

| Page | Classe | Role |
| --- | --- | --- |
| Dashboard | `DashboardPage` | Statistiques |
| Tous les livres | `ManageBooksPage` | Catalogue, ajout, modification, suppression, emprunt |
| Recommandations | `RecommendationsPage` | Livres similaires |
| Livres les plus empruntes | `ActionTablePage` | Classement par nombre d'emprunts |
| Auteurs | `ManageAuthorsPage` | Liste et ajout d'auteurs |
| Emprunts | `ActionTablePage` | Emprunts actifs |
| Retards | `ActionTablePage` | Livres en retard |
| Historique personnel | `ActionTablePage` | Historique du compte |
| Mes emprunts admin | `ActionTablePage` | Emprunts du compte admin |
| Utilisateurs | `ActionTablePage` | Comptes et promotion admin |
| Mon Profil | `ProfilePage` | Informations personnelles et mot de passe |

Les pages `Mes emprunts admin` et `Utilisateurs` sont reservees a l'admin.

## 10. Gestion des livres

Fichiers concernes :

- `views/main_window.py`
- `controllers/livre_controller.py`
- `models/livre.py`

### Ajouter un livre

Accessible a l'admin.

Flux :

1. L'admin remplit titre, auteur, categorie, annee, description et mots cles.
2. Le bouton Ajouter appelle `ManageBooksPage.on_add()`.
3. La page appelle `LivreController.add_livre()`.
4. Le controller verifie que le titre et l'auteur sont presents.
5. Il retrouve l'auteur via son identifiant.
6. Il verifie que le meme livre n'existe pas deja pour le meme auteur.
7. Il cree un objet `Livre`.
8. Il sauvegarde la table `livres`.
9. La page est rechargee.

### Modifier un livre

Flux :

1. L'admin selectionne une ligne.
2. `on_selection()` remplit le formulaire.
3. Le bouton Modifier appelle `on_update()`.
4. Le controller verifie que le livre existe.
5. Il refuse la modification si elle cree un doublon.
6. Les champs sont mis a jour.

### Supprimer un livre

Flux :

1. L'admin selectionne un livre.
2. Le bouton Supprimer demande confirmation.
3. `LivreController.delete_livre()` verifie le livre.
4. Si le livre est emprunte, la suppression est refusee.
5. Si le livre est disponible, il est supprime.

## 11. Gestion des auteurs

Fichiers concernes :

- `views/main_window.py`
- `controllers/livre_controller.py`
- `models/auteur.py`

Flux d'ajout :

1. L'admin saisit nom, prenom et nationalite.
2. `ManageAuthorsPage.on_add()` appelle `LivreController.add_auteur()`.
3. Le nom est obligatoire.
4. Le doublon nom + prenom est refuse.
5. L'auteur est sauvegarde dans `auteurs`.

## 12. Emprunter un livre

Fichiers concernes :

- `views/main_window.py`
- `controllers/emprunt_controller.py`
- `models/emprunt.py`
- `models/utilisateur.py`

Flux :

1. L'utilisateur selectionne un livre.
2. Il clique sur Emprunter.
3. `ManageBooksPage.on_borrow()` appelle `emprunter_livre_pour_compte()`.
4. Le controller verifie que le compte est connecte.
5. Il charge la table `livres`.
6. Il verifie que le livre existe.
7. Il verifie que le livre est disponible.
8. Il trouve ou cree le profil utilisateur.
9. Il cree un emprunt avec le statut `Actif`.
10. Il calcule `date_limite` avec une duree de 14 jours.
11. Il sauvegarde l'emprunt.
12. Il met le livre en statut emprunte.

La constante importante est :

```python
DUREE_EMPRUNT_JOURS = 14
```

## 13. Retourner un livre

Flux :

1. L'utilisateur va dans Emprunts ou Retards.
2. Il selectionne un livre.
3. Il clique sur Retourner.
4. `MainWindow.return_callback()` appelle `retourner_livre_pour_compte()`.
5. Le controller retrouve l'utilisateur lie au compte.
6. Il cherche un emprunt `Actif` pour ce livre et cet utilisateur.
7. Si aucun emprunt actif n'existe, l'action est refusee.
8. Sinon, l'emprunt passe a `Cloture`.
9. La date de retour est remplie.
10. Le livre repasse a `Disponible`.

## 14. Retards

Un retard est detecte quand :

- l'emprunt est encore `Actif` ;
- la `date_limite` est depassee.

Methodes importantes :

- `get_livres_en_retard()`
- `get_livres_en_retard_pour_compte(compte)`
- `_get_livres_en_retard_actifs(id_utilisateur=None)`

Le nombre de jours de retard est calcule dans le controller.

## 15. Historique personnel

L'historique charge tous les emprunts du compte connecte.

Il peut afficher :

- les livres encore empruntes ;
- les livres en retard ;
- les livres retournes.

Les donnees sont enrichies avec les informations du livre et de l'auteur.

## 16. Recommandation de livres

Fichiers concernes :

- `views/main_window.py`
- `controllers/livre_controller.py`
- `services/recommendation_service.py`

Flux :

1. L'utilisateur ouvre la page Recommandations.
2. La liste deroulante contient tous les livres.
3. L'utilisateur choisit un livre.
4. Il clique sur Recommander.
5. `LivreController.get_livres_recommandes()` charge tous les livres.
6. `RecommendationService.recommend_by_book()` calcule les similarites.
7. Les resultats sont affiches avec un score.

Champs utilises :

- `titre`
- `auteur`
- `categorie`
- `description`
- `mots_cles`

Si `scikit-learn` est disponible, le service utilise `TfidfVectorizer` et `cosine_similarity`.

Si `scikit-learn` n'est pas disponible, le service utilise une solution interne de secours :

- tokenisation ;
- calcul TF ;
- calcul IDF ;
- cosine similarity.

## 17. Profil utilisateur

Fichiers concernes :

- `views/profile_page.py`
- `controllers/profile_controller.py`
- `controllers/auth_controller.py`

La page profil permet de :

- modifier le username ;
- modifier nom, prenom et email ;
- modifier le mot de passe.

Flux de modification du profil :

1. L'utilisateur modifie les champs.
2. Le username et le nom sont obligatoires.
3. Si le username change, `AuthController.update_username()` est appele.
4. Le profil est mis a jour avec `ProfileController.update_profile()`.
5. Le nom affiche dans la sidebar est mis a jour.

Flux de mot de passe :

1. L'utilisateur saisit ancien mot de passe.
2. Il saisit nouveau mot de passe et confirmation.
3. Les deux nouveaux champs doivent correspondre.
4. `AuthController.update_password()` verifie l'ancien mot de passe.
5. Un nouveau salt et un nouveau hash sont sauvegardes.

## 18. Roles et droits

### Utilisateur normal

Un utilisateur normal peut :

- consulter le dashboard ;
- consulter les livres ;
- emprunter un livre ;
- retourner ses livres ;
- consulter ses emprunts ;
- consulter ses retards ;
- consulter son historique ;
- utiliser les recommandations ;
- modifier son profil ;
- changer son mot de passe.

### Administrateur

Un admin peut faire tout ce qu'un utilisateur normal peut faire, plus :

- ajouter des livres ;
- modifier des livres ;
- supprimer des livres disponibles ;
- ajouter des auteurs ;
- consulter tous les emprunts ;
- consulter tous les retards ;
- voir les comptes ;
- rendre un utilisateur admin.

## 19. Regles metier importantes

| Regle | Ou elle est appliquee |
| --- | --- |
| Un username doit etre unique | `AuthController.create_account()` et `update_username()` |
| Le mot de passe est stocke hashe | `AuthController._hash_password()` |
| Un livre doit avoir un titre et un auteur | `LivreController.add_livre()` |
| Le meme livre ne peut pas etre ajoute deux fois pour le meme auteur | `LivreController._ensure_livre_unique()` |
| Un livre emprunte ne peut pas etre supprime | `LivreController.delete_livre()` |
| Un livre deja emprunte ne peut pas etre reemprunte | `EmpruntController.emprunter_livre()` |
| Un retour doit correspondre a un emprunt actif | `EmpruntController.retourner_livre()` |
| Un retard depend de la date limite | `EmpruntController._get_livres_en_retard_actifs()` |

## 20. Ou modifier le projet

| Besoin | Fichier a modifier |
| --- | --- |
| Changer le style | `views/style.py` |
| Ajouter un bouton dans la sidebar | `views/main_window.py` |
| Ajouter une page | `views/main_window.py` ou nouveau fichier dans `views/` |
| Modifier la connexion | `views/login_dialog.py` et `controllers/auth_controller.py` |
| Modifier les livres | `controllers/livre_controller.py` |
| Modifier les emprunts | `controllers/emprunt_controller.py` |
| Modifier les recommandations | `services/recommendation_service.py` |
| Ajouter une colonne MySQL | `data/database.py` |
| Ajouter un champ dans un objet | fichier correspondant dans `models/` |

## 21. Parcours rapide pour lire le projet

Pour comprendre le projet sans se perdre, lis dans cet ordre :

1. `README.md` pour l'installation et le lancement.
2. `main.py` pour comprendre le demarrage.
3. `views/login_dialog.py` pour la connexion.
4. `views/main_window.py` pour comprendre la navigation.
5. `controllers/auth_controller.py` pour les comptes.
6. `controllers/livre_controller.py` pour livres et auteurs.
7. `controllers/emprunt_controller.py` pour emprunts, retours et retards.
8. `services/recommendation_service.py` pour les recommandations.
9. `data/database.py` pour MySQL et les tables.
10. `DIAGRAMMES_PLANTUML.md` pour les diagrammes UML.

## 22. Resume mental du projet

Le projet fonctionne comme ceci :

```text
main.py
  -> affiche LoginDialog
  -> authentifie via AuthController
  -> ouvre MainWindow
  -> la sidebar affiche les pages
  -> les pages appellent les controllers
  -> les controllers lisent/ecrivent avec Database
  -> Database communique avec MySQL
  -> RecommendationService calcule les livres similaires
```

Si tu comprends cette chaine, tu comprends le coeur du projet.


# TalkZone -- Projet de Demonstration de Cybersecurite

TalkZone est une application web simulant un forum de discussion communautaire fonctionnel (dark theme, systeme de posts, commentaires, profils, panel admin). 
Cependant, sous son apparence legitime, cette application a ete specialement concue avec une **vulnerabilite critique intentionnelle** pour servir de support a une demonstration d'attaque informatique.

## 🎯 Objectif du Projet

Ce projet a pour but de demontrer une attaque de type **"0-click"** permettant a un attaquant de se connecter en tant qu'administrateur sans aucune interaction avec la victime, en exploitant une faille dans la generation des tokens d'authentification (CWE-330 : Utilisation d'une resolution cryptographique previsible).

## 🚀 Fonctionnalites du Forum

*   **Design Moderne** : Interface en mode sombre (Dark Theme) avec des composants en "glassmorphism", responsive et epuree.
*   **Authentification** : Inscription et Connexion.
*   **Posts et Commentaires** : Creation de sujets de discussion avec categories (General, Technique, Cybersecurite, etc.) et systeme de commentaires.
*   **Profils Utilisateurs** : Modification du pseudo, email, et bio. Affichage des statistiques (nombre de posts, commentaires).
*   **Dashboard Admin** : Interface reservee aux administrateurs pour voir les statistiques globales et supprimer des utilisateurs.

## ⚠️ La Vulnerabilite (ATTENTION - SPOILER)

La vulnerabilite reside dans le mecanisme de creation du token de session (`auth_token` dans les cookies), gere par la fonction `make_token` dans `app/app.py`.

Le token n'est pas un UUID aleatoire et securise, mais un hash SHA-256 base sur des **donnees totalement previsibles** :
1.  L'ID de l'utilisateur en hexadecimal (ex: `1` pour id 1, `2` pour id 2, etc.)
2.  Le pseudo (username) de l'utilisateur (publiquement visible sur le forum).
3.  Une tranche horaire de 6 heures basee sur l'heure du serveur (`YYYY-MM-DD-HH` ou HH est `00`, `06`, `12` ou `18`).

**Vecteur d'attaque :**
Un attaquant souhaitant usurper l'identite de l'administrateur (dont le pseudo est generalement connu, ex: `admin`, et dont l'ID peut etre devine, ex: `3`) peut generer lui-meme le hash SHA-256 de la chaine `3|admin|2026-05-11-18`, inserer ce hash dans ses cookies (`auth_token`), et rafraichir la page pour obtenir instantanement les droits administrateur.

## 🛠️ Installation et Lancement

Le projet est entierement dockerise pour un deploiement simple.

### Prerequis
*   Docker
*   Docker Compose

### Commandes

1.  Cloner le repertoire.
2.  Lancer les conteneurs en arriere-plan :
    ```bash
    docker-compose up --build -d
    ```
3.  L'application sera accessible sur : **http://localhost:5000**
4.  Pour arreter l'application :
    ```bash
    docker-compose down
    ```

## 👥 Comptes de Test (Base de donnees initiale)

La base de donnees est peuplee automatiquement avec des utilisateurs et des posts pour simuler une activite.
*Note: Les accents ont ete retires pour assurer une stabilite parfaite de l'encodage.*

| Pseudo  | Mot de passe | Role  | ID (info utile pour l'attaque) |
| :---    | :---         | :---  | :--- |
| marie   | mariepwd     | user  | 1 |
| paul    | paulpwd      | user  | 2 |
| **admin** | **adminpwd**   | **admin** | **3** |
| sarah   | sarahpwd     | user  | 4 |
| lucas   | lucaspwd     | user  | 5 |



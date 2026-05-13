# TalkZone - Projet de Demonstration de Cybersecurite

TalkZone est une application web simulant un forum de discussion communautaire fonctionnel (theme sombre, systeme de posts, commentaires, profils, panel administrateur). 
Sous son apparence legitime, cette application a ete specialement concue avec une vulnerabilite critique intentionnelle pour servir de support a une demonstration d'attaque informatique.

## Objectif du Projet

Ce projet a pour but de demontrer une attaque de type "0-click" permettant a un attaquant de se connecter en tant qu'administrateur sans aucune interaction avec la victime. Cette attaque exploite une faille dans la generation des jetons d'authentification (CWE-330 : Utilisation d'une resolution cryptographique previsible).

## Fonctionnalites du Forum

*   Design Moderne : Interface en mode sombre (Dark Theme) avec des composants en glassmorphism, responsive et epuree.
*   Authentification : Inscription et Connexion.
*   Posts et Commentaires : Creation de sujets de discussion avec categories (General, Technique, Cybersecurite, etc.) et systeme de commentaires.
*   Profils Utilisateurs : Modification du pseudo, email, et bio. Affichage des statistiques (nombre de posts, commentaires) et de l'ID utilisateur.
*   Dashboard Administrateur : Interface reservee aux administrateurs pour visualiser les statistiques globales et gerer les utilisateurs.

## La Vulnerabilite (Explication technique)

La vulnerabilite reside dans le mecanisme de creation du jeton de session (auth_token dans les cookies), gere par la fonction make_token dans app/app.py.

Le jeton n'est pas un identifiant aleatoire securise, mais un hachage SHA-256 base sur des donnees totalement previsibles :
1.  L'ID de l'utilisateur en format hexadecimal (exemple : 1 pour l'ID 1, 3 pour l'ID 3).
2.  Le pseudo (username) de l'utilisateur, publiquement visible sur le forum.
3.  La date du jour au format YYYY-MM-DD.

Vecteur d'attaque :
Un attaquant souhaitant usurper l'identite de l'administrateur peut aisement forger ce jeton. Sachant que le pseudo de la cible est "admin", que son ID est 3, et en utilisant la date courante (par exemple 2026-05-11), l'attaquant genere lui-meme le hachage SHA-256 de la chaine "3|admin|2026-05-11".
En inserant ce hachage manuellement dans ses cookies (auth_token) et en rafraichissant la page, l'attaquant obtient instantanement les droits d'administration sur la plateforme.

## Installation et Lancement

Le projet est entierement dockerise pour garantir un deploiement uniforme.

Prerequis :
*   Docker

Commandes de lancement :

1.  Cloner le repertoire du projet.
2.  Lancer les conteneurs en arriere-plan :
    ```bash
    docker-compose up --build -d
    ```
3.  L'application sera accessible sur : http://localhost:5000
4.  Pour arreter l'application :
    ```bash
    docker-compose down
    ```

## Comptes de Test (Base de donnees)

La base de donnees est peuplee lors de l'initialisation avec des utilisateurs et des posts pour simuler une activite reelle. Afin d'eviter tout probleme d'encodage, les caracteres accentues ont ete retires.

| Pseudo  | Mot de passe | Role  | ID (requis pour l'attaque) |
| :---    | :---         | :---  | :--- |
| marie   | mariepwd     | user  | 1 |
| paul    | paulpwd      | user  | 2 |
| admin   | adminpwd     | admin | 3 |
| sarah   | sarahpwd     | user  | 4 |
| lucas   | lucaspwd     | user  | 5 |

## Avertissement

Cette application est volontairement vulnerable. Elle ne doit en aucun cas etre deployee sur un serveur public ou en environnement de production. Elle est strictement reservee a un usage educatif et de demonstration technique dans un environnement isole.

# TalkZone — Token d'Authentification Prévisible

> Application web volontairement vulnérable développée dans le cadre d'un projet de cybersécurité à **EMINES School of Industrial Management, UM6P**.

---

## À propos

TalkZone est un forum de discussion communautaire conçu pour démontrer une attaque **0-click** exploitant une vulnérabilité de type **token d'authentification prévisible** (CWE-330).

L'attaque permet à un attaquant d'usurper l'identité de l'administrateur **sans interaction avec la victime**, en recalculant son token de session à partir d'informations publiques.

> Pour le détail complet de la vulnérabilité et de l'exploitation, voir le rapport technique.

---

## Stack technique

| Composant | Technologie |
|:---|:---|
| Backend | Python 3 / Flask |
| Base de données | MySQL |
| Templates | Jinja2 |
| Conteneurisation | Docker |

---

## Installation

**Prérequis :** Docker

```bash
# Lancer l'application
docker-compose up --build -d

# Accéder à l'application
http://localhost:5000

# Arrêter l'application
docker-compose down
```

---

## Comptes de test

| ID | Pseudo | Mot de passe | Rôle |
|:---|:---|:---|:---|
| 1 | marie | mariepwd | user |
| 2 | paul | paulpwd | user |
| **3** | **admin** | **adminpwd** | **admin** |
| 4 | sarah | sarahpwd | user |
| 5 | lucas | lucaspwd | user |

---

*Projet P05 — Red Team — EMINES UM6P — 2025/2026*
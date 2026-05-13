import hashlib
from datetime import datetime

# --- Paramètres connus (à adapter) ---
user_id = 3  # identifiant numérique connu
username = "admin"  # pseudo connu
target_token = "174e53c4ca27b3ce60813e534cd59ca5a319728435ae84c3871b62624de130fe"  # hash à retrouver

# Date du jour (ou une date fixe pour les tests)
#now = datetime.now()
#date_obj = now.date()
# Pour reproduire l'exemple, on peut aussi forcer une date :
date_obj = datetime(2026, 5, 12).date()

# --- Préparation des valeurs à tester ---
# ID : en décimal (3) ou en hexadécimal (3 -> "3")
id_decimal = str(user_id)
id_hex = format(user_id, 'x')  # "3"

# Username : inchangé
username_str = username

# Formats de date possibles (sans heure)
date_formats = {
    "YYYY-MM-DD": date_obj.strftime("%Y-%m-%d"),
    "DD/MM/YYYY": date_obj.strftime("%d/%m/%Y"),
    "YYYYMMDD": date_obj.strftime("%Y%m%d"),
    "DD-MM-YYYY": date_obj.strftime("%d-%m-%Y"),
}

# Séparateurs possibles (peut être vide)
separators = ["|", "_", ":", "-", ""]

# Ordres possibles des 3 éléments (id, username, date)
from itertools import permutations

orders = list(permutations(["id", "username", "date"]))

# --- Recherche exhaustive ---
print("=" * 70)
print(f"Recherche du token pour : id={user_id} ({id_hex}), username='{username}', date={date_obj}")
print(f"Hash cible : {target_token}\n")

found = False
for id_style in [("dec", id_decimal), ("hex", id_hex)]:
    id_label, id_val = id_style
    for fmt_name, date_val in date_formats.items():
        for sep in separators:
            for order in orders:
                # Construction de la chaîne brute selon l'ordre
                parts = []
                for elem in order:
                    if elem == "id":
                        parts.append(id_val)
                    elif elem == "username":
                        parts.append(username_str)
                    else:  # date
                        parts.append(date_val)
                raw = sep.join(parts)
                token = hashlib.sha256(raw.encode()).hexdigest()

                # Affichage compact
                print(f"Test : '{raw}' -> {token}")

                if token == target_token:
                    print("\n TOKEN TROUVÉ !")
                    print(f"  Chaîne brute : {raw}")
                    print(f"  ID utilisé   : {id_label} ({id_val})")
                    print(f"  Format date  : {fmt_name} ({date_val})")
                    print(f"  Séparateur   : '{sep}'")
                    print(f"  Ordre        : {' | '.join(order)}")
                    print(f"  Token        : {token}")
                    found = True
                    break
            if found:
                break
        if found:
            break
    if found:
        break

if not found:
    print("\n Aucune combinaison trouvée. Vérifiez le token cible et les paramètres.")
print("=" * 70)
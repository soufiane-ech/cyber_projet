# Étape 1 : Partir d'une image Python officielle
FROM python:3.11-slim

# Étape 2 : Définir le dossier de travail dans le container
WORKDIR /app

# Étape 3 : Copier le fichier des dépendances
COPY app/requirements.txt .

# Étape 4 : Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Étape 5 : Copier tout le code de l'application
COPY app/ .

# Étape 6 : Exposer le port 5000 (Flask)
EXPOSE 5000

# Étape 7 : Commande à lancer quand le container démarre
CMD ["python", "app.py"]
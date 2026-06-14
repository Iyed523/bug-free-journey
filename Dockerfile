# On utilise l'image officielle de Microsoft qui contient déjà Python et le navigateur Chromium
FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# On définit le dossier de travail
WORKDIR /app

# On copie le fichier des dépendances
COPY requirements.txt .

# On installe FastAPI, Uvicorn, etc.
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le reste de ton code (main.py, etc.)
COPY . .

# On expose le port 8000
EXPOSE 8000

# La commande pour démarrer ton serveur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
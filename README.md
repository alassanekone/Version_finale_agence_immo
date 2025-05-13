# Application de Gestion Immobilière

Cette application Django permet de gérer les biens immobiliers, les locations, les ventes et les clients.

## Fonctionnalités

- Gestion des propriétés (terrains, immeubles, appartements)
- Gestion des biens (location et vente)
- Gestion des clients (locataires et acheteurs)
- Gestion des locations
- Suivi des paiements
- Gestion des dépenses
- Géolocalisation des biens

## Installation

1. Cloner le projet
2. Créer un environnement virtuel :
   ```bash
   python -m venv venv
   ```
3. Activer l'environnement virtuel :
   ```bash
   # Windows
   venv\Scripts\activate
   ```
4. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
5. Effectuer les migrations :
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
6. Créer un superutilisateur :
   ```bash
   python manage.py createsuperuser
   ```
7. Lancer le serveur :
   ```bash
   python manage.py runserver
   ```

## Technologies utilisées

- Backend : Django (Python)
- Frontend : HTML, CSS, JavaScript, Bootstrap
- Base de données : SQLite
- Géolocalisation : OpenStreetMap

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Agence_immobiliere.settings')
django.setup()

from django.contrib.auth.models import User

# Créer le superutilisateur si il n'existe pas déjà
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

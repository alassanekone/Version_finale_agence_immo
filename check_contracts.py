import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Agence_immobiliere.settings')
django.setup()

from gestion_immobiliere.models import Location, Paiement
from django.utils import timezone
from django.db.models import Max

def check_payment_delays():
    print("\n=== VÉRIFICATION DES RETARDS DE PAIEMENT ===")
    today = timezone.now().date()
    active_contracts = Location.objects.filter(statut='Actif', type_operation='location')
    
    for contract in active_contracts:
        # Récupérer le dernier paiement
        last_payment = Paiement.objects.filter(
            location=contract,
            type_paiement='loyer'
        ).aggregate(Max('date_paiement'))
        
        last_payment_date = last_payment['date_paiement__max']
        if not last_payment_date:
            print(f"!!! ALERTE: Aucun paiement enregistré pour le contrat {contract.id}")
            print(f"   Client: {contract.client.nom} {contract.client.prenom}")
            print("")
            continue
        
        # Calculer le retard en jours
        delay = (today - last_payment_date).days - 30  # Considérant un mois de 30 jours
        if delay > 0:
            print(f"!!! RETARD DE PAIEMENT: {delay} jours")
            print(f"   Contrat ID: {contract.id}")
            print(f"   Client: {contract.client.nom} {contract.client.prenom}")
            print(f"   Dernier paiement: {last_payment_date}\n")

def check_expiring_contracts():
    print("\n=== CONTRATS EXPIRANT DANS LES 90 JOURS ===")
    today = timezone.now().date()
    expiration_date = today + timedelta(days=90)
    
    print(f"Date aujourd'hui: {today}")
    print(f"Date limite: {expiration_date}")
    
    # Afficher tous les contrats pour déboguer
    print("\nListe de tous les contrats dans la base:")
    all_contracts = Location.objects.all()
    for contract in all_contracts:
        print(f"ID: {contract.id}, Client: {contract.client.nom}, "
              f"Date début: {contract.date_debut}, Date fin: {contract.date_fin}, "
              f"Statut: {contract.statut}, Type: {contract.type_operation}")
    
    print("\nContrats expirant bientôt:")
    # Modification de la requête pour inclure tous les contrats qui expirent bientôt
    expiring_contracts = Location.objects.filter(
        date_fin__range=[today, expiration_date]
    ).order_by('date_fin')
    
    for contract in expiring_contracts:
        days_remaining = (contract.date_fin - today).days
        print(f"!!! EXPIRATION DANS {days_remaining} JOURS:")
        print(f"   Contrat ID: {contract.id}")

        print(f"   Client: {contract.client.nom} {contract.client.prenom}")
        print(f"   Date début: {contract.date_debut}")
        print(f"   Date fin: {contract.date_fin}")
        print(f"   Type: {contract.get_type_operation_display()}")
        print(f"   Statut: {contract.statut}\n")

if __name__ == '__main__':
    today = timezone.now().date()
    print(f"\nDate d'aujourd'hui: {today}")
    check_payment_delays()
    check_expiring_contracts()

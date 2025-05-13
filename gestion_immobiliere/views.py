from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, Http404
from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.template.defaultfilters import date as date_filter
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from xhtml2pdf import pisa

from .models import Propriete, Beaux, Tiers, Location, Depense, Paiement, Document, CompteBancaire, Transaction, RapportFinancier
from .forms import ProprieteForm, BeauxForm, TiersForm, LocationForm, DepenseForm, PaiementForm, DocumentForm, RapportFinancierForm
from datetime import datetime, timedelta
from django.conf import settings
import json
from decimal import Decimal

@login_required
def dashboard(request):
    """Vue pour le tableau de bord"""
    from django.db.models import Sum, Count
    
    # Statistiques des locations
    revenus_mensuels = Location.objects.filter(type_operation='location').aggregate(
        total=Sum('montant_location')
    )['total'] or 0

    # Statistiques des ventes
    revenus_ventes = Location.objects.filter(type_operation='vente').aggregate(
        total=Sum('montant_location')
    )['total'] or 0

    # Nombre de biens par type
    biens_par_type = Propriete.objects.values('type_beaux').annotate(
        total=Count('id_propriete')
    ).order_by('type_beaux')

    # Nombre de clients par type
    clients_par_type = Tiers.objects.values('type').annotate(
        total=Count('id_tiers')
    ).order_by('type')

    # Statistiques générales
    total_proprietes = Propriete.objects.count()
    total_biens = Beaux.objects.count()
    total_tiers = Tiers.objects.count()
    locations_actives = Location.objects.filter(type_operation='location').count()

    # Dernières locations
    dernieres_locations = Location.objects.select_related('bien', 'client').order_by('-created_at')[:5]

    context = {
        'revenus_mensuels': revenus_mensuels,
        'revenus_ventes': revenus_ventes,
        'biens_par_type': biens_par_type,
        'clients_par_type': clients_par_type,
        'total_proprietes': total_proprietes,
        'total_biens': total_biens,
        'total_tiers': total_tiers,
        'locations_actives': locations_actives,
        'dernieres_locations': dernieres_locations,
    }

    return render(request, 'gestion_immobiliere/dashboard.html', context)

@login_required
def proprietes_list(request):
    proprietes = Propriete.objects.all().order_by('-date_aquisition')
    return render(request, 'gestion_immobiliere/proprietes_list.html', {'proprietes': proprietes})

@login_required
def ajouter_propriete(request):
    if request.method == 'POST':
        form = ProprieteForm(request.POST, request.FILES)
        if form.is_valid():
            propriete = form.save()
            messages.success(request, 'Propriété ajoutée avec succès.')
            return redirect('proprietes')
    else:
        form = ProprieteForm()
    return render(request, 'gestion_immobiliere/propriete_form.html', {'form': form, 'titre': 'Ajouter une propriété'})

@login_required
def modifier_propriete(request, pk):
    propriete = get_object_or_404(Propriete, pk=pk)
    if request.method == 'POST':
        form = ProprieteForm(request.POST, request.FILES, instance=propriete)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propriété modifiée avec succès.')
            return redirect('proprietes')
    else:
        form = ProprieteForm(instance=propriete)
    return render(request, 'gestion_immobiliere/propriete_form.html', {'form': form, 'titre': 'Modifier la propriété'})

@login_required
def propriete_detail(request, pk):
    """Vue pour le détail d'une propriété"""
    propriete = get_object_or_404(Propriete, pk=pk)
    biens = Beaux.objects.filter(id_propriete=propriete)
    depenses = Depense.objects.filter(id_propriete=propriete).order_by('-date')
    content_type = ContentType.objects.get_for_model(Propriete)
    documents = Document.objects.filter(
        content_type=content_type,
        object_id=propriete.pk
    )
    
    # Calcul des statistiques
    total_depenses = depenses.aggregate(Sum('montant'))['montant__sum'] or 0
    biens_disponibles = biens.filter(statut='disponible').count()
    
    # Calcul des revenus mensuels
    revenus_mensuels = sum(
        location.montant_location
        for bien in biens
        for location in Location.objects.filter(id_beaux=bien, statut='actif')
    )
    
    # Préparation des coordonnées GPS
    try:
        lat, lng = map(float, propriete.coordonnees_gps.split(','))
    except (ValueError, AttributeError):
        lat, lng = 0, 0

    context = {
        'propriete': propriete,
        'biens': biens,
        'depenses': depenses,
        'documents': documents,
        'total_depenses': total_depenses,
        'biens_disponibles': biens_disponibles,
        'revenus_mensuels': revenus_mensuels,
        'lat': lat,
        'lng': lng
    }
    
    return render(request, 'gestion_immobiliere/propriete_detail.html', context)

@login_required
def biens_list(request):
    biens = Beaux.objects.all().order_by('reference')
    return render(request, 'gestion_immobiliere/biens_list.html', {'biens': biens})

@login_required
def ajouter_bien(request):
    if request.method == 'POST':
        form = BeauxForm(request.POST)
        if form.is_valid():
            bien = form.save()
            messages.success(request, 'Bien ajouté avec succès.')
            return redirect('biens')
    else:
        form = BeauxForm()
    return render(request, 'gestion_immobiliere/beaux_form.html', {'form': form, 'titre': 'Ajouter un bien'})

@login_required
def modifier_bien(request, pk):
    bien = get_object_or_404(Beaux, pk=pk)
    if request.method == 'POST':
        form = BeauxForm(request.POST, instance=bien)
        if form.is_valid():
            bien = form.save()
            messages.success(request, 'Bien modifié avec succès.')
            return redirect('biens')
    else:
        form = BeauxForm(instance=bien)
    return render(request, 'gestion_immobiliere/beaux_form.html', {'form': form, 'titre': f'Modifier le bien {bien.reference}'})

@login_required
def tiers_list(request):
    tiers = Tiers.objects.all().order_by('telephone')
    return render(request, 'gestion_immobiliere/tiers_list.html', {'tiers': tiers})

@login_required
def ajouter_tiers(request):
    """Vue pour ajouter un nouveau tiers"""
    if request.method == 'POST':
        form = TiersForm(request.POST)
        if form.is_valid():
            tiers = form.save()
            messages.success(request, 'Tiers ajouté avec succès.')
            return redirect('tiers_list')
    else:
        form = TiersForm()
    
    return render(request, 'gestion_immobiliere/tiers_form.html', {
        'form': form,
        'titre': 'Nouveau tiers'
    })

@login_required
def modifier_tiers(request, pk):
    """Vue pour modifier un tiers existant"""
    tiers = get_object_or_404(Tiers, pk=pk)
    if request.method == 'POST':
        form = TiersForm(request.POST, instance=tiers)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tiers modifié avec succès.')
            return redirect('tiers')
    else:
        form = TiersForm(instance=tiers)
    
    return render(request, 'gestion_immobiliere/tiers_form.html', {
        'form': form,
        'titre': 'Modifier le tiers'
    })

@login_required
def tiers_detail(request, pk):
    """Vue pour afficher les détails d'un tiers"""
    tiers = get_object_or_404(Tiers, pk=pk)
    proprietes = tiers.proprietes.all() if tiers.type == 'proprietaire' else None
    locations = Location.objects.filter(client=tiers) if tiers.type in ['locataire', 'acheteur'] else None
    
    context = {
        'tiers': tiers,
        'proprietes': proprietes,
        'locations': locations,
    }
    return render(request, 'gestion_immobiliere/tiers_detail.html', context)

@login_required
def ajouter_tiers_ajax(request):
    """Vue pour ajouter un tiers via AJAX"""
    if request.method == 'POST':
        try:
            tiers = Tiers.objects.create(
                type=request.POST.get('type'),
                mail=request.POST.get('mail'),
                telephone=request.POST.get('telephone'),
                adresse1=request.POST.get('adresse1'),
                pieces=request.POST.get('pieces')
            )
            return JsonResponse({
                'status': 'success',
                'tiers_id': tiers.id_tiers,
                'tiers_name': f"{tiers.mail} - {tiers.telephone}"
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)

@login_required
def locations_list(request):
    """Vue pour afficher la liste des locations et ventes"""
    locations = Location.objects.select_related('id_beaux', 'client').order_by('-date_debut')
    
    # Calculer les montants pour chaque location/vente
    for location in locations:
        # Calculer le montant total
        if location.type_operation == 'location':
            location.montant_total = location.montant_location * location.nombre_periodes
        else:
            location.montant_total = location.montant_location
            
        # Calculer le montant payé
        location.montant_paye = location.paiements.aggregate(total=Sum('montant'))['total'] or 0
        location.montant_restant = location.montant_total - location.montant_paye
        
        # Déterminer le statut de paiement
        if location.montant_restant <= 0:
            location.statut_paiement = 'complet'
        elif location.montant_paye > 0:
            location.statut_paiement = 'partiel'
        else:
            location.statut_paiement = 'impaye'
    
    context = {
        'locations': locations,
        'today': timezone.now().date(),
    }
    return render(request, 'gestion_immobiliere/locations_list.html', context)

@login_required
def ajouter_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            bien = location.id_beaux
            
            # Mettre à jour le statut du bien en fonction du type d'opération
            if location.type_operation == 'location':
                bien.statut = 'loue'
            elif location.type_operation == 'vente':
                bien.statut = 'vendu'
            
            bien.save()
            location.save()
            
            messages.success(request, 'La location a été créée avec succès.')
            return redirect('locations')
    else:
        form = LocationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'gestion_immobiliere/location_form.html', context)

@login_required
def modifier_location(request, pk):
    location = get_object_or_404(Location, pk=pk)
    
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            nouvelle_location = form.save(commit=False)
            
            # Si le bien a changé, mettre à jour les statuts
            if nouvelle_location.id_beaux != location.id_beaux:
                # Remettre l'ancien bien en disponible
                location.id_beaux.statut = 'disponible'
                location.id_beaux.save()
                
                # Mettre à jour le statut du nouveau bien
                if nouvelle_location.type_operation == 'location':
                    nouvelle_location.id_beaux.statut = 'loue'
                else:
                    nouvelle_location.id_beaux.statut = 'vendu'
                nouvelle_location.id_beaux.save()
            
            nouvelle_location.save()
            messages.success(request, 'La location a été modifiée avec succès.')
            return redirect('locations')
    else:
        form = LocationForm(instance=location)
    
    context = {
        'form': form,
        'titre': 'Modifier la location'
    }
    return render(request, 'gestion_immobiliere/location_form.html', context)

@login_required
def location_detail(request, pk):
    """Vue pour afficher les détails d'une location ou vente avec gestion des paiements"""
    location = get_object_or_404(Location.objects.select_related('id_beaux', 'client'), pk=pk)
    paiements = Paiement.objects.filter(location=location).order_by('-date_paiement')
    
    # Calcul des montants
    montant_total = location.montant_location * location.nombre_periodes if location.type_operation == 'location' else location.montant_location
    montant_paye = paiements.aggregate(total=Sum('montant'))['total'] or 0
    montant_restant = montant_total - montant_paye
    
    # Formulaire de paiement pour le modal
    form_paiement = PaiementForm()
    
    # Documents liés
    content_type = ContentType.objects.get_for_model(Location)
    documents = Document.objects.filter(
        content_type=content_type,
        object_id=location.id
    )
    
    context = {
        'location': location,
        'paiements': paiements,
        'montant_total': montant_total,
        'montant_paye': montant_paye,
        'montant_restant': montant_restant,
        'form_paiement': form_paiement,
        'documents': documents,
    }
    
    return render(request, 'gestion_immobiliere/location_detail.html', context)

@login_required
def resilier_location(request, pk):
    location = get_object_or_404(Location, pk=pk)
    
    if request.method == 'POST':
        date_resiliation = request.POST.get('date_resiliation')
        motif_resiliation = request.POST.get('motif_resiliation')
        
        if date_resiliation and motif_resiliation:
            # La méthode resilier s'occupe déjà de la restitution de la caution
            location.resilier(date_resiliation, motif_resiliation)
            messages.success(request, 'Le contrat a été résilié avec succès.')
            return redirect('location_detail', pk=location.pk)
    
    context = {
        'location': location,
        'titre': 'Résilier le contrat'
    }
    return render(request, 'gestion_immobiliere/resilier_location.html', context)

@login_required
def depenses_list(request):
    """Vue pour afficher la liste des dépenses"""
    from django.db.models import Sum, Avg
    from django.db.models.functions import ExtractMonth, ExtractYear
    from datetime import datetime
    
    # Récupérer toutes les dépenses triées par date
    depenses = Depense.objects.all().order_by('-date')
    
    # Calculer le total des dépenses
    total = depenses.aggregate(total=Sum('montant'))['total'] or 0
    
    # Calculer la moyenne mensuelle des dépenses
    moyenne_mensuelle = depenses.aggregate(avg=Avg('montant'))['avg'] or 0
    
    # Calculer les dépenses du mois en cours
    mois_actuel = datetime.now().month
    annee_actuelle = datetime.now().year
    depenses_mois = depenses.filter(
        date__month=mois_actuel,
        date__year=annee_actuelle
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Données pour le graphique
    depenses_par_mois = depenses.annotate(
        mois=ExtractMonth('date'),
        annee=ExtractYear('date')
    ).values('mois', 'annee').annotate(
        total=Sum('montant')
    ).order_by('annee', 'mois')
    
    # Préparer les données pour le graphique
    dates = []
    montants = []
    for item in depenses_par_mois:
        dates.append(f"{item['mois']}/{item['annee']}")
        montants.append(str(float(item['total'])))
    
    context = {
        'depenses': depenses,
        'total': "{:.0f}".format(total),
        'moyenne_mensuelle': "{:.0f}".format(moyenne_mensuelle),
        'depenses_mois': "{:.0f}".format(depenses_mois),
        'dates': dates,
        'montants': montants
    }
    
    return render(request, 'gestion_immobiliere/depenses_list.html', context)

@login_required
def ajouter_depense(request):
    initial = {}
    if 'propriete_id' in request.GET:
        initial['propriete'] = request.GET['propriete_id']

    if request.method == 'POST':
        form = DepenseForm(request.POST)
        if form.is_valid():
            depense = form.save()
            messages.success(request, 'Dépense ajoutée avec succès.')
            return redirect('depenses')
    else:
        form = DepenseForm(initial=initial)
    
    return render(request, 'gestion_immobiliere/depense_form.html', {
        'form': form,
        'titre': 'Ajouter une dépense'
    })

@login_required
def modifier_depense(request, pk):
    depense = get_object_or_404(Depense, pk=pk)
    if request.method == 'POST':
        form = DepenseForm(request.POST, instance=depense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dépense modifiée avec succès.')
            return redirect('depenses')
    else:
        form = DepenseForm(instance=depense)
    
    return render(request, 'gestion_immobiliere/depense_form.html', {
        'form': form,
        'titre': 'Modifier une dépense'
    })

@login_required
def supprimer_depense(request, pk):
    """Vue pour supprimer une dépense"""
    depense = get_object_or_404(Depense, pk=pk)
    if request.method == 'POST':
        if depense.transaction:
            depense.transaction.delete()
        depense.delete()
        messages.success(request, 'Dépense supprimée avec succès.')
        return redirect('depenses')
    return redirect('depenses')

@login_required
def ajouter_paiement(request, pk):
    """Vue pour ajouter un paiement à une location"""
    location = get_object_or_404(Location, pk=pk)
    
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.location = location
            paiement.save()
            messages.success(request, 'Le paiement a été ajouté avec succès.')
            return redirect('location_detail', pk=pk)
        else:
            messages.error(request, 'Erreur lors de l\'ajout du paiement. Veuillez vérifier les informations saisies.')
            return redirect('location_detail', pk=pk)
    
    return redirect('location_detail', pk=pk)

@login_required
def supprimer_paiement(request, pk):
    """Vue pour supprimer un paiement"""
    paiement = get_object_or_404(Paiement, pk=pk)
    location_id = paiement.location.id
    
    if request.method == 'POST':
        paiement.delete()
        messages.success(request, 'Le paiement a été supprimé avec succès.')
    
    return redirect('location_detail', pk=location_id)

@login_required
def modifier_paiement(request, pk):
    """Vue pour modifier un paiement existant"""
    paiement = get_object_or_404(Paiement, pk=pk)
    
    if request.method == 'POST':
        form = PaiementForm(request.POST, instance=paiement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Le paiement a été modifié avec succès.')
            return redirect('liste_paiements')
    else:
        form = PaiementForm(instance=paiement)
    
    context = {
        'form': form,
        'paiement': paiement,
        'titre': 'Modifier le paiement'
    }
    return render(request, 'gestion_immobiliere/paiement_form.html', context)

@login_required
def supprimer_paiement(request, pk):
    """Vue pour supprimer un paiement"""
    paiement = get_object_or_404(Paiement, pk=pk)
    
    if request.method == 'POST':
        paiement.delete()
        messages.success(request, 'Le paiement a été supprimé avec succès.')
        return redirect('liste_paiements')
    
    context = {
        'paiement': paiement,
        'titre': 'Supprimer le paiement'
    }
    return render(request, 'gestion_immobiliere/confirm_delete.html', context)

@login_required
def ajouter_document(request, model_name, object_id):
    model_mapping = {
        'propriete': Propriete,
        'location': Location,
        'tiers': Tiers,
    }
    
    if model_name not in model_mapping:
        messages.error(request, 'Type d\'objet non valide.')
        return redirect('dashboard')
        
    Model = model_mapping[model_name]
    obj = get_object_or_404(Model, pk=object_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.content_type = ContentType.objects.get_for_model(Model)
            document.object_id = obj.pk
            document.save()
            messages.success(request, 'Document ajouté avec succès.')
            return redirect(f'{model_name}s')
    else:
        form = DocumentForm()
        
    return render(request, 'gestion_immobiliere/document_form.html', {
        'form': form,
        'objet': obj,
        'titre': 'Ajouter un document'
    })

@login_required
def supprimer_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Document supprimé avec succès.')
        return redirect('dashboard')
    return render(request, 'gestion_immobiliere/confirmer_suppression.html', {
        'objet': document,
        'titre': 'Supprimer le document'
    })

@login_required
def get_bien_prix(request, bien_id):
    """Vue pour récupérer le prix d'un bien"""
    from django.http import JsonResponse
    bien = get_object_or_404(Beaux, id_beaux=bien_id)
    return JsonResponse({'prix': str(bien.prix)})

@login_required
def statistiques_json(request):
    """Vue pour fournir les données des graphiques en JSON"""
    # Statistiques des propriétés par type
    stats_proprietes = Propriete.objects.values('type_propriete').annotate(
        total=Count('id_propriete')
    )
    
    # Revenus mensuels sur les 6 derniers mois
    six_mois = timezone.now() - timedelta(days=180)
    revenus_mensuels = Location.objects.filter(
        date_paiement__gte=six_mois
    ).values('date_paiement__month').annotate(
        total=Sum('prix_mensuel')
    ).order_by('date_paiement__month')
    
    # Dépenses par catégorie
    depenses_categories = Depense.objects.values('categorie').annotate(
        total=Sum('montant')
    )
    
    return JsonResponse({
        'proprietes': list(stats_proprietes),
        'revenus': list(revenus_mensuels),
        'depenses': list(depenses_categories)
    })

@login_required
def imprimer_contrat_location(request, pk):
    """Vue pour imprimer un contrat de location"""
    location = get_object_or_404(Location, pk=pk)
    if location.type_operation != 'location':
        raise Http404("Ce n'est pas un contrat de location")
        
    context = {
        'location': location,
        'date': datetime.now(),
    }
    
    template = get_template('gestion_immobiliere/contrat_location.html')
    html = template.render(context)
    
    # Création du PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=contrat_location_{pk}.pdf'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la création du PDF')
    return response

@login_required
def imprimer_contrat_vente(request, pk):
    """Vue pour imprimer un contrat de vente"""
    location = get_object_or_404(Location, pk=pk)
    if location.type_operation != 'vente':
        raise Http404("Ce n'est pas un contrat de vente")
        
    context = {
        'vente': location,
        'date': datetime.now(),
    }
    
    template = get_template('gestion_immobiliere/contrat_vente.html')
    html = template.render(context)
    
    # Création du PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=contrat_vente_{pk}.pdf'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la création du PDF')
    return response

@login_required
def comptabilite_dashboard(request):
    """Vue pour afficher le tableau de bord de la comptabilité"""
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Obtenir la date actuelle
    today = timezone.now().date()
    
    # Calculer le début du mois et de l'année en cours
    debut_mois = today.replace(day=1)
    debut_annee = today.replace(month=1, day=1)
    
    # Récupérer tous les paiements
    paiements_mois = Paiement.objects.filter(
        date_paiement__range=(debut_mois, today)
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    paiements_annee = Paiement.objects.filter(
        date_paiement__range=(debut_annee, today)
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Récupérer toutes les dépenses
    depenses_mois = Depense.objects.filter(
        date__range=(debut_mois, today)
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    depenses_annee = Depense.objects.filter(
        date__range=(debut_annee, today)
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Calculer les soldes
    solde_mois = paiements_mois - depenses_mois
    solde_annee = paiements_annee - depenses_annee
    
    # Récupérer les derniers paiements et dépenses
    derniers_paiements = Paiement.objects.select_related('location').order_by('-date_paiement')[:5]
    dernieres_depenses = Depense.objects.order_by('-date')[:5]
    
    # Récupérer les derniers rapports
    derniers_rapports = RapportFinancier.objects.order_by('-date_generation')[:5]
    
    context = {
        'paiements_mois': paiements_mois,
        'paiements_annee': paiements_annee,
        'depenses_mois': depenses_mois,
        'depenses_annee': depenses_annee,
        'solde_mois': solde_mois,
        'solde_annee': solde_annee,
        'derniers_paiements': derniers_paiements,
        'dernieres_depenses': dernieres_depenses,
        'derniers_rapports': derniers_rapports,
    }
    
    return render(request, 'gestion_immobiliere/comptabilite_dashboard.html', context)

@login_required
def generer_rapport(request):
    if request.method == 'POST':
        form = RapportFinancierForm(request.POST)
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut']
            date_fin = form.cleaned_data['date_fin']
            periode = form.cleaned_data['periode']
            commentaires = form.cleaned_data.get('commentaires', '')
            
            # Récupérer les paiements dans l'intervalle
            paiements = Paiement.objects.filter(
                date_paiement__range=(date_debut, date_fin)
            ).select_related('transaction')
            
            # Récupérer les dépenses dans l'intervalle
            depenses = Depense.objects.filter(
                date__range=(date_debut, date_fin)
            ).select_related('transaction')
            
            # Calculer les totaux
            total_revenus = paiements.aggregate(total=Sum('montant'))['total'] or 0
            total_depenses = depenses.aggregate(total=Sum('montant'))['total'] or 0
            solde_net = total_revenus - total_depenses
            
            # Créer le rapport
            rapport = RapportFinancier.objects.create(
                date_debut=date_debut,
                date_fin=date_fin,
                periode=periode,
                total_revenus=total_revenus,
                total_depenses=total_depenses,
                solde_net=solde_net,
                commentaires=commentaires
            )
            
            messages.success(request, "Le rapport financier a été généré avec succès.")
            return redirect('rapport_detail', pk=rapport.pk)
    else:
        form = RapportFinancierForm()
    
    return render(request, 'gestion_immobiliere/rapport_form.html', {'form': form})

@login_required
def rapport_detail(request, pk):
    rapport = get_object_or_404(RapportFinancier, pk=pk)
    
    if request.method == 'POST':
        form = RapportFinancierForm(request.POST, instance=rapport)
        if form.is_valid():
            rapport = form.save()
            rapport.actualiser_totaux()
            messages.success(request, "Le rapport a été mis à jour avec succès.")
            return redirect('rapport_detail', pk=rapport.pk)
    else:
        form = RapportFinancierForm(instance=rapport)
    
    # Récupérer les paiements et dépenses pour la période
    paiements = Paiement.objects.filter(
        date_paiement__range=(rapport.date_debut, rapport.date_fin)
    ).select_related('transaction')
    
    depenses = Depense.objects.filter(
        date__range=(rapport.date_debut, rapport.date_fin)
    ).select_related('transaction')
    
    context = {
        'rapport': rapport,
        'form': form,
        'paiements': paiements,
        'depenses': depenses,
        'total_revenus': rapport.total_revenus,
        'total_depenses': rapport.total_depenses,
        'solde_net': rapport.solde_net
    }
    
    # Si c'est une demande d'impression, utiliser un template différent
    if 'print' in request.GET:
        return render(request, 'gestion_immobiliere/rapport_print.html', context)
    
    return render(request, 'gestion_immobiliere/rapport_detail.html', context)

@login_required
def liste_rapports(request):
    """Vue pour lister tous les rapports financiers"""
    rapports = RapportFinancier.objects.all()
    
    context = {
        'rapports': rapports,
        'title': "Liste des rapports financiers"
    }
    
    return render(request, 'gestion_immobiliere/rapports_list.html', context)

@login_required
def liste_paiements(request):
    """Vue pour afficher la liste des paiements"""
    paiements = Paiement.objects.select_related('location').order_by('-date_paiement')
    
    context = {
        'paiements': paiements,
    }
    return render(request, 'gestion_immobiliere/liste_paiements.html', context)

@login_required
def liste_depenses(request):
    """Vue pour afficher la liste des dépenses"""
    depenses = Depense.objects.order_by('-date')
    
    context = {
        'depenses': depenses,
    }
    return render(request, 'gestion_immobiliere/liste_depenses.html', context)

@login_required
def depense_detail(request, pk):
    """Vue pour afficher les détails d'une dépense"""
    depense = get_object_or_404(Depense, pk=pk)
    return render(request, 'gestion_immobiliere/depense_detail.html', {
        'depense': depense
    })

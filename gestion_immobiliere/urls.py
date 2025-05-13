from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # URLs pour les propriétés
    path('proprietes/', views.proprietes_list, name='proprietes'),
    path('propriete/ajouter/', views.ajouter_propriete, name='ajouter_propriete'),
    path('propriete/<int:pk>/', views.propriete_detail, name='propriete_detail'),
    path('propriete/<int:pk>/modifier/', views.modifier_propriete, name='modifier_propriete'),
    
    # URLs pour les biens
    path('biens/', views.biens_list, name='biens'),
    path('bien/ajouter/', views.ajouter_bien, name='ajouter_bien'),
    path('bien/<int:pk>/modifier/', views.modifier_bien, name='modifier_bien'),
    path('bien/<int:bien_id>/prix/', views.get_bien_prix, name='get_bien_prix'),
    
    # URLs pour les tiers
    path('tiers/', views.tiers_list, name='tiers_list'),
    path('tiers/ajouter/', views.ajouter_tiers, name='ajouter_tiers'),
    path('tiers/<int:pk>/', views.tiers_detail, name='tiers_detail'),
    path('tiers/<int:pk>/modifier/', views.modifier_tiers, name='modifier_tiers'),
    path('tiers/ajouter/ajax/', views.ajouter_tiers_ajax, name='ajouter_tiers_ajax'),
    
    # URLs pour les locations
    path('locations/', views.locations_list, name='locations'),
    path('location/ajouter/', views.ajouter_location, name='ajouter_location'),
    path('location/<int:pk>/', views.location_detail, name='location_detail'),
    path('location/<int:pk>/modifier/', views.modifier_location, name='modifier_location'),
    path('location/<int:pk>/resilier/', views.resilier_location, name='resilier_location'),
    path('location/<int:pk>/imprimer-contrat-location/', views.imprimer_contrat_location, name='imprimer_contrat_location'),
    path('location/<int:pk>/imprimer-contrat-vente/', views.imprimer_contrat_vente, name='imprimer_contrat_vente'),
    
    # URLs pour les paiements
    path('paiements/', views.liste_paiements, name='liste_paiements'),
    path('location/<int:pk>/paiement/ajouter/', views.ajouter_paiement, name='ajouter_paiement'),
    path('paiement/<int:pk>/modifier/', views.modifier_paiement, name='modifier_paiement'),
    path('paiement/<int:pk>/supprimer/', views.supprimer_paiement, name='supprimer_paiement'),
    
    # URLs pour les dépenses
    path('depenses/', views.depenses_list, name='depenses'),
    path('depense/ajouter/', views.ajouter_depense, name='ajouter_depense'),
    path('depense/<int:pk>/', views.depense_detail, name='depense_detail'),
    path('depense/<int:pk>/modifier/', views.modifier_depense, name='modifier_depense'),
    path('depense/<int:pk>/supprimer/', views.supprimer_depense, name='supprimer_depense'),
    
    # URLs pour les documents
    path('<str:model_name>/<int:object_id>/document/ajouter/', views.ajouter_document, name='ajouter_document'),
    path('document/<int:pk>/supprimer/', views.supprimer_document, name='supprimer_document'),
    
    # URLs pour les statistiques
    path('api/statistiques/', views.statistiques_json, name='statistiques_json'),
    
    # URLs pour la comptabilité
    path('comptabilite/', views.comptabilite_dashboard, name='comptabilite'),
    path('comptabilite/rapports/', views.liste_rapports, name='rapports'),
    path('comptabilite/rapport/generer/', views.generer_rapport, name='generer_rapport'),
    path('comptabilite/rapport/<int:pk>/', views.rapport_detail, name='rapport_detail'),
    path('comptabilite/paiements/', views.liste_paiements, name='paiements'),
    path('comptabilite/depenses/', views.liste_depenses, name='liste_depenses'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

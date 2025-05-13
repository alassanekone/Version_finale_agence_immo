from django.contrib import admin
from .models import Propriete, Beaux, Tiers, Location, Depense, CompteBancaire, Transaction, RapportFinancier

# Register your models here.

@admin.register(Propriete)
class ProprieteAdmin(admin.ModelAdmin):
    list_display = ('reference', 'type_beaux', 'categorie', 'localisation', 'superficie')
    list_filter = ('type_beaux', 'categorie', 'usage')
    search_fields = ('reference', 'localisation')
    date_hierarchy = 'date_aquisition'

@admin.register(Beaux)
class BeauxAdmin(admin.ModelAdmin):
    list_display = ('reference', 'id_propriete', 'prix', 'statut')
    list_filter = ('statut',)
    search_fields = ('reference',)

@admin.register(Tiers)
class TiersAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'type', 'telephone', 'mail')
    list_filter = ('type',)
    search_fields = ('mail', 'telephone')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin pour la gestion des locations"""
    list_display = ['id', 'id_beaux', 'client', 'type_operation', 'montant_location', 'date_debut', 'date_fin', 'statut']
    list_filter = ['type_operation', 'statut']
    search_fields = ['id_beaux__designation', 'client__nom', 'client__prenom']
    date_hierarchy = 'date_debut'

@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'montant', 'date']
    list_filter = ['date']
    search_fields = ['description']
    ordering = ['-date']

@admin.register(CompteBancaire)
class CompteBancaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'numero_compte', 'solde', 'date_modification')
    search_fields = ('nom', 'numero_compte')
    readonly_fields = ('solde', 'date_creation', 'date_modification')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'compte', 'type_transaction', 'montant', 'date_transaction')
    list_filter = ('type_transaction', 'date_transaction', 'compte')
    search_fields = ('reference', 'description')
    readonly_fields = ('reference', 'date_transaction')
    ordering = ('-date_transaction',)

@admin.register(RapportFinancier)
class RapportFinancierAdmin(admin.ModelAdmin):
    list_display = ('get_periode_display', 'date_debut', 'date_fin', 'total_revenus', 'total_depenses', 'solde_net')
    list_filter = ('periode', 'date_generation')
    readonly_fields = ('total_revenus', 'total_depenses', 'solde_net', 'date_generation')
    ordering = ('-date_generation',)

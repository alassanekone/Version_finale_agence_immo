from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta
from django.db.models import Sum

# Create your models here.

class Propriete(models.Model):
    """Modèle pour la gestion des propriétés immobilières"""
    TYPES_BEAUX = [
        ('terrain', 'Terrain'),
        ('immeuble', 'Immeuble'),
        ('appartement', 'Appartement'),
    ]
    
    CATEGORIES = [
        ('location', 'Location'),
        ('vente', 'Vente'),
        ('mixte', 'Mixte'),
    ]
    
    USAGES = [
        ('residentiel', 'Résidentiel'),
        ('commercial', 'Commercial'),
        ('mixte', 'Mixte'),
    ]

    id_propriete = models.AutoField(primary_key=True)
    reference = models.CharField(max_length=50, unique=True)
    type_beaux = models.CharField(max_length=20, choices=TYPES_BEAUX)
    date_aquisition = models.DateField()
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    localisation = models.TextField()
    coordonnees_gps = models.CharField(max_length=100)
    superficie = models.DecimalField(max_digits=10, decimal_places=2)
    usage = models.CharField(max_length=20, choices=USAGES)
    description = models.TextField()
    proprietaire = models.ForeignKey('Tiers', on_delete=models.SET_NULL, null=True, blank=True, related_name='proprietes')
    documents = GenericRelation('Document')

    def __str__(self):
        return f"{self.reference} - {self.type_beaux}"

class Beaux(models.Model):
    """Modèle pour la gestion des biens immobiliers"""
    STATUTS = [
        ('disponible', 'Disponible'),
        ('loue', 'Loué'),
        ('vendu', 'Vendu'),
    ]

    id_beaux = models.AutoField(primary_key=True)
    id_propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE)
    reference = models.CharField(max_length=50, unique=True)
    prix = models.DecimalField(max_digits=12, decimal_places=0, help_text='Montant en XOF')
    statut = models.CharField(max_length=20, choices=STATUTS)
    documents = GenericRelation('Document')

    def __str__(self):
        return f"{self.reference} - {self.statut}"

class Tiers(models.Model):
    """Modèle pour la gestion des tiers (locataires, acheteurs, propriétaires)"""
    TYPES_TIERS = [
        ('locataire', 'Locataire'),
        ('acheteur', 'Acheteur'),
        ('proprietaire', 'Propriétaire d\'immeuble'),
    ]

    CIVILITE_CHOICES = [
        ('M', 'Monsieur'),
        ('Mme', 'Madame'),
        ('Mlle', 'Mademoiselle'),
    ]

    id_tiers = models.AutoField(primary_key=True)
    civilite = models.CharField(max_length=4, choices=CIVILITE_CHOICES, default='M')
    nom = models.CharField(max_length=100, default='')
    prenom = models.CharField(max_length=100, default='')
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, blank=True)
    nationalite = models.CharField(max_length=50, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    pieces = models.IntegerField(verbose_name="Nombre de pièces souhaitées", default=1, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPES_TIERS, default='locataire')
    adresse1 = models.TextField(verbose_name="Adresse actuelle", default='')
    adresse2 = models.TextField(blank=True, null=True, verbose_name="Adresse complémentaire")
    telephone = models.CharField(max_length=20, default='')
    telephone2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone secondaire")
    mail = models.EmailField(default='')
    piece_identite = models.FileField(upload_to='pieces_identite/%Y/%m/', blank=True, null=True, verbose_name="Pièce d'identité")
    numero_piece_identite = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro de pièce d'identité")
    date_validite_piece = models.DateField(null=True, blank=True, verbose_name="Date de validité de la pièce d'identité")
    nom_employeur = models.CharField(max_length=100, blank=True, null=True)
    adresse_employeur = models.TextField(blank=True, null=True)
    telephone_employeur = models.CharField(max_length=20, blank=True, null=True)
    revenu_mensuel = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, help_text='Montant en XOF')
    date_creation = models.DateTimeField(default=timezone.now)
    date_modification = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    documents = GenericRelation('Document')

    class Meta:
        verbose_name = 'Tiers'
        verbose_name_plural = 'Tiers'
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.civilite} {self.nom} {self.prenom}"

    def get_full_name(self):
        return f"{self.civilite} {self.nom} {self.prenom}"

class Location(models.Model):
    """Modèle pour gérer les locations et ventes de biens"""
    TYPE_OPERATION_CHOICES = [
        ('location', 'Location'),
        ('vente', 'Vente'),
    ]
    PERIODICITE_CHOICES = [
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('semestriel', 'Semestriel'),
        ('annuel', 'Annuel'),
    ]
    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('resilié', 'Résilié'),
        ('terminé', 'Terminé'),
    ]

    id_beaux = models.ForeignKey(Beaux, on_delete=models.CASCADE, verbose_name="Bien immobilier", null=True, blank=True)
    client = models.ForeignKey(Tiers, on_delete=models.CASCADE, null=True, blank=True)
    type_operation = models.CharField(max_length=20, choices=TYPE_OPERATION_CHOICES, default='location')
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin", null=True, blank=True)
    montant_location = models.IntegerField(verbose_name="Montant de la location/vente (XOF)")
    periodicite = models.CharField(max_length=20, choices=PERIODICITE_CHOICES, default='mensuel')
    nombre_periodes = models.IntegerField(verbose_name="Nombre de périodes", default=12)
    caution = models.IntegerField(verbose_name="Montant de la caution (XOF)", default=0)
    avance = models.IntegerField(verbose_name="Montant des avances (XOF)", default=0)
    frais_agence = models.IntegerField(verbose_name="Frais d'agence (XOF)", default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='actif')
    date_resiliation = models.DateField(verbose_name="Date de résiliation", null=True, blank=True)
    motif_resiliation = models.TextField(verbose_name="Motif de résiliation", blank=True)
    caution_restituee = models.BooleanField(verbose_name="Caution restituée", default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_type_operation_display()} - {self.id_beaux} - {self.client}"

    def save(self, *args, **kwargs):
        if self.type_operation == 'location':
            if not self.date_fin:
                # Calculer la date de fin en fonction de la périodicité et du nombre de périodes
                if self.periodicite == 'mensuel':
                    self.date_fin = self.date_debut + timedelta(days=30 * self.nombre_periodes)
                elif self.periodicite == 'trimestriel':
                    self.date_fin = self.date_debut + timedelta(days=90 * self.nombre_periodes)
                elif self.periodicite == 'semestriel':
                    self.date_fin = self.date_debut + timedelta(days=180 * self.nombre_periodes)
                elif self.periodicite == 'annuel':
                    self.date_fin = self.date_debut + timedelta(days=365 * self.nombre_periodes)
        
        super().save(*args, **kwargs)

    def resilier(self, date_resiliation, motif):
        """Résilier le contrat et restituer la caution"""
        # Mettre à jour le statut du bien
        if self.id_beaux:
            self.id_beaux.statut = 'disponible'
            self.id_beaux.save()

        # Mettre à jour le contrat
        self.statut = 'resilié'
        self.date_resiliation = date_resiliation
        self.motif_resiliation = motif
        
        # Créer un paiement pour la restitution de la caution si elle n'a pas déjà été restituée
        if not self.caution_restituee and self.caution > 0:
            from .models import Paiement
            Paiement.objects.create(
                location=self,
                montant=-self.caution,  # Montant négatif car c'est une restitution
                date_paiement=date_resiliation,
                type_paiement='restitution_caution',
                description=f"Restitution de la caution suite à la résiliation du contrat. Motif : {motif}"
            )
            self.caution_restituee = True
        
        self.save()

class Paiement(models.Model):
    """Modèle pour les paiements des locations"""
    TYPE_PAIEMENT_CHOICES = [
        ('loyer', 'Loyer'),
        ('caution', 'Caution'),
        ('avance', 'Avance'),
        ('frais_agence', 'Frais d\'agence'),
        ('restitution_caution', 'Restitution de caution'),
    ]
    
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='paiements')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateField()
    type_paiement = models.CharField(max_length=50, choices=TYPE_PAIEMENT_CHOICES, default='loyer')
    description = models.TextField(blank=True)
    transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Paiement de {self.montant} XOF - {self.location}"

    def save(self, *args, **kwargs):
        # Créer ou mettre à jour la transaction associée
        compte = CompteBancaire.objects.first()
        if compte and not self.transaction:
            self.transaction = Transaction.objects.create(
                compte=compte,
                type_transaction='credit',
                montant=self.montant,
                description=f"Paiement location - {self.location}",
                date_transaction=self.date_paiement
            )
            compte.crediter(self.montant, f"Paiement location - {self.location}")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Supprimer la transaction associée
        if self.transaction:
            compte = self.transaction.compte
            compte.solde -= self.montant
            compte.save()
            self.transaction.delete()
        super().delete(*args, **kwargs)

class Depense(models.Model):
    """Modèle pour les dépenses"""
    id_depense = models.AutoField(primary_key=True)
    id_propriete = models.ForeignKey(Propriete, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=200)
    transaction = models.OneToOneField('Transaction', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"
        ordering = ['-date']

    def __str__(self):
        return f"Dépense du {self.date} - {self.montant} XOF"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.transaction:
            self.transaction.delete()
        super().delete(*args, **kwargs)

class Document(models.Model):
    """Modèle pour gérer les documents et photos"""
    id_document = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=100)
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    type_document = models.CharField(max_length=20, choices=[
        ('photo', 'Photo'),
        ('contrat', 'Contrat'),
        ('facture', 'Facture'),
        ('autre', 'Autre'),
    ])
    date_upload = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    # Relations polymorphiques
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-date_upload']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return self.titre

class CompteBancaire(models.Model):
    """Modèle pour gérer le compte bancaire de l'agence"""
    nom = models.CharField(max_length=100)
    numero_compte = models.CharField(max_length=50, unique=True)
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compte bancaire"
        verbose_name_plural = "Comptes bancaires"

    def __str__(self):
        return f"{self.nom} - {self.numero_compte}"

    def crediter(self, montant, description=""):
        """Créditer le compte"""
        self.solde += montant
        self.save()
        Transaction.objects.create(
            compte=self,
            type_transaction='credit',
            montant=montant,
            description=description
        )

    def debiter(self, montant, description=""):
        """Débiter le compte"""
        if self.solde >= montant:
            self.solde -= montant
            self.save()
            Transaction.objects.create(
                compte=self,
                type_transaction='debit',
                montant=montant,
                description=description
            )
            return True
        return False

class Transaction(models.Model):
    """Modèle pour enregistrer toutes les transactions"""
    TYPES_TRANSACTION = [
        ('credit', 'Crédit'),
        ('debit', 'Débit'),
    ]

    compte = models.ForeignKey(CompteBancaire, on_delete=models.CASCADE, related_name='transactions')
    type_transaction = models.CharField(max_length=10, choices=TYPES_TRANSACTION)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    date_transaction = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    reference = models.CharField(max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['-date_transaction']

    def __str__(self):
        return f"{self.get_type_transaction_display()} - {self.montant} XOF"

    def save(self, *args, **kwargs):
        if not self.reference:
            # Générer une référence unique
            prefix = 'CR' if self.type_transaction == 'credit' else 'DB'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            self.reference = f"{prefix}{timestamp}"
        super().save(*args, **kwargs)

class RapportFinancier(models.Model):
    """Modèle pour générer et stocker les rapports financiers"""
    PERIODES = [
        ('jour', 'Journalier'),
        ('semaine', 'Hebdomadaire'),
        ('mois', 'Mensuel'),
        ('trimestre', 'Trimestriel'),
        ('annee', 'Annuel'),
    ]

    date_debut = models.DateField()
    date_fin = models.DateField()
    periode = models.CharField(max_length=20, choices=PERIODES)
    total_revenus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_depenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    solde_net = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_generation = models.DateTimeField(auto_now_add=True)
    commentaires = models.TextField(blank=True)

    class Meta:
        verbose_name = "Rapport financier"
        verbose_name_plural = "Rapports financiers"
        ordering = ['-date_generation']

    def __str__(self):
        return f"Rapport du {self.date_debut} au {self.date_fin}"

    def actualiser_totaux(self):
        """Actualise les totaux du rapport"""
        from django.db.models import Sum
        
        # Calculer le total des revenus
        total_revenus = Paiement.objects.filter(
            date_paiement__range=(self.date_debut, self.date_fin)
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        # Calculer le total des dépenses
        total_depenses = Depense.objects.filter(
            date__range=(self.date_debut, self.date_fin)
        ).aggregate(total=Sum('montant'))['total'] or 0
        
        # Mettre à jour les champs
        self.total_revenus = total_revenus
        self.total_depenses = total_depenses
        self.solde_net = total_revenus - total_depenses
        self.save()

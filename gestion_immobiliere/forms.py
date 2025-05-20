from django import forms
from django.core.validators import FileExtensionValidator
from django.db import models
from .models import Propriete, Beaux, Tiers, Location, Depense, Paiement, Document, CompteBancaire, RapportFinancier

class ProprieteForm(forms.ModelForm):
    """Formulaire pour la gestion des propriétés"""
    class Meta:
        model = Propriete
        fields = [
            'reference', 'type_beaux', 'date_aquisition', 'categorie',
            'localisation', 'coordonnees_gps', 'superficie', 'usage', 'description'
        ]
        widgets = {
            'date_aquisition': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_superficie(self):
        superficie = self.cleaned_data['superficie']
        if superficie <= 0:
            raise forms.ValidationError("La superficie doit être supérieure à 0.")
        return superficie

    def clean_coordonnees_gps(self):
        coords = self.cleaned_data['coordonnees_gps']
        if coords:
            try:
                lat, lon = map(float, coords.split(','))
                if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                    raise forms.ValidationError("Coordonnées GPS invalides.")
            except ValueError:
                raise forms.ValidationError("Format des coordonnées GPS invalide.")
        return coords

class BeauxForm(forms.ModelForm):
    """Formulaire pour la gestion des biens"""
    class Meta:
        model = Beaux
        fields = ['id_propriete', 'reference', 'prix', 'statut']
        widgets = {
            'prix': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': 'Entrez le prix'
            }),
            'reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez la référence unique'
            }),
            'id_propriete': forms.Select(attrs={
                'class': 'form-control'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'id_propriete': 'Propriété',
            'reference': 'Référence',
            'prix': 'Prix',
            'statut': 'Statut'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les propriétés disponibles
        self.fields['id_propriete'].queryset = Propriete.objects.all().order_by('reference')

    def clean_prix(self):
        prix = self.cleaned_data['prix']
        if prix <= 0:
            raise forms.ValidationError("Le prix doit être supérieur à 0.")
        return prix

    def clean_reference(self):
        reference = self.cleaned_data['reference']
        if not reference:
            raise forms.ValidationError("La référence est obligatoire.")
        
        # Vérifier si la référence existe déjà
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            # Si on modifie un bien existant, exclure sa propre référence de la vérification
            exists = Beaux.objects.exclude(pk=instance.pk).filter(reference=reference).exists()
        else:
            # Pour un nouveau bien
            exists = Beaux.objects.filter(reference=reference).exists()
            
        if exists:
            raise forms.ValidationError("Cette référence existe déjà.")
            
        return reference

class TiersForm(forms.ModelForm):
    """Formulaire pour la gestion des tiers"""
    class Meta:
        model = Tiers
        fields = [
            'civilite', 'nom', 'prenom', 
            'date_naissance', 'nationalite',
            'type',
            'adresse1', 'telephone', 'mail'
        ]
        widgets = {
            'civilite': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'nom': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nom de famille'
                }
            ),
            'prenom': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Prénom'
                }
            ),
            'date_naissance': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),
            'nationalite': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Nationalité'
                }
            ),
            'type': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'adresse1': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Adresse'
                }
            ),
            'telephone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Téléphone'
                }
            ),
            'mail': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Adresse email'
                }
            )
        }

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone')
        if telephone:
            # Supprimer tous les caractères non numériques
            telephone = ''.join(filter(str.isdigit, telephone))
            # Vérifier la longueur
            if len(telephone) != 8:
                raise forms.ValidationError("Le numéro de téléphone doit contenir 8 chiffres.")
        return telephone

class LocationForm(forms.ModelForm):
    """Formulaire pour la gestion des locations"""
    class Meta:
        model = Location
        fields = ['id_beaux', 'client', 'type_operation', 'date_debut', 'date_fin',
                 'montant_location', 'periodicite', 'nombre_periodes', 'caution',
                 'avance', 'frais_agence', 'notes']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'montant_location': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'caution': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'avance': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'frais_agence': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        labels = {
            'id_beaux': 'Référence du Bien',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialiser les champs avec des valeurs par défaut
        self.fields['caution'].initial = 0
        self.fields['avance'].initial = 0
        self.fields['frais_agence'].initial = 0
        self.fields['nombre_periodes'].initial = 12
        self.fields['periodicite'].initial = 'mensuel'
        
        # Si c'est une modification, inclure le bien actuel dans les choix
        instance = kwargs.get('instance')
        if instance and instance.id_beaux:
            self.fields['id_beaux'].queryset = Beaux.objects.filter(
                models.Q(statut='disponible') | models.Q(pk=instance.id_beaux.pk)
            )
        else:
            self.fields['id_beaux'].queryset = Beaux.objects.filter(statut='disponible')

    def clean(self):
        cleaned_data = super().clean()
        type_operation = cleaned_data.get('type_operation')
        periodicite = cleaned_data.get('periodicite')
        nombre_periodes = cleaned_data.get('nombre_periodes')
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if type_operation == 'vente':
            # Pour une vente, forcer la périodicité à "unique" et le nombre de périodes à 1
            cleaned_data['periodicite'] = 'mensuel'
            cleaned_data['nombre_periodes'] = 1
            
            # Pour une vente, la date de fin doit être égale à la date de début
            if date_debut:
                cleaned_data['date_fin'] = date_debut
        else:
            # Pour une location, vérifier que les dates sont cohérentes
            if date_debut and date_fin and date_fin < date_debut:
                raise forms.ValidationError("La date de fin doit être postérieure à la date de début.")

        return cleaned_data

class DepenseForm(forms.ModelForm):
    """Formulaire pour la gestion des dépenses"""
    class Meta:
        model = Depense
        fields = ['id_propriete', 'description', 'montant', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'id_propriete': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_propriete'].queryset = Propriete.objects.all().order_by('reference')

class PaiementForm(forms.ModelForm):
    """Formulaire pour la gestion des paiements"""
    class Meta:
        model = Paiement
        fields = ['location', 'montant', 'date_paiement', 'type_paiement', 'description']
        widgets = {
            'location': forms.Select(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_paiement': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type_paiement': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }

    def clean_montant(self):
        montant = self.cleaned_data['montant']
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")
        return montant

class DocumentForm(forms.ModelForm):
    """Formulaire pour l'ajout et la modification des documents"""
    class Meta:
        model = Document
        fields = ['titre', 'fichier', 'type_document', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fichier'].validators.append(
            FileExtensionValidator(
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
            )
        )

    def clean_fichier(self):
        fichier = self.cleaned_data['fichier']
        if fichier and fichier.size > 10 * 1024 * 1024:  # 10MB limit
            raise forms.ValidationError("La taille du fichier ne doit pas dépasser 10MB.")
        return fichier

class CompteBancaireForm(forms.ModelForm):
    class Meta:
        model = CompteBancaire
        fields = ['nom', 'numero_compte']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_compte': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RapportFinancierForm(forms.ModelForm):
    """Formulaire pour générer un rapport financier"""
    class Meta:
        model = RapportFinancier
        fields = ['date_debut', 'date_fin', 'periode', 'commentaires']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'periode': forms.Select(attrs={'class': 'form-control'}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")
        
        return cleaned_data

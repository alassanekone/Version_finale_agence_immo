from django.db import migrations, models
import django.utils.timezone

def transfer_locataire_to_tiers(apps, schema_editor):
    Locataire = apps.get_model('gestion_immobiliere', 'Locataire')
    Tiers = apps.get_model('gestion_immobiliere', 'Tiers')
    
    for locataire in Locataire.objects.all():
        Tiers.objects.create(
            id_tiers=locataire.id_locataire,
            civilite=locataire.civilite,
            nom=locataire.nom,
            prenom=locataire.prenom,
            date_naissance=locataire.date_naissance,
            lieu_naissance=locataire.lieu_naissance,
            nationalite=locataire.nationalite,
            profession=locataire.profession,
            telephone=locataire.telephone,
            telephone2=locataire.telephone2,
            mail=locataire.mail,
            adresse1=locataire.adresse1,
            adresse2=locataire.adresse2,
            piece_identite=locataire.piece_identite,
            numero_piece_identite=locataire.numero_piece_identite,
            date_validite_piece=locataire.date_validite_piece,
            nom_employeur=locataire.nom_employeur,
            telephone_employeur=locataire.telephone_employeur,
            adresse_employeur=locataire.adresse_employeur,
            revenu_mensuel=locataire.revenu_mensuel,
            notes=locataire.notes,
            type=locataire.type
        )

class Migration(migrations.Migration):

    dependencies = [
        ('gestion_immobiliere', '0013_alter_depense_options_alter_paiement_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tiers',
            fields=[
                ('id_tiers', models.AutoField(primary_key=True, serialize=False)),
                ('civilite', models.CharField(choices=[('M', 'Monsieur'), ('Mme', 'Madame'), ('Mlle', 'Mademoiselle')], default='M', max_length=4)),
                ('nom', models.CharField(default='', max_length=100)),
                ('prenom', models.CharField(default='', max_length=100)),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('lieu_naissance', models.CharField(blank=True, max_length=100)),
                ('nationalite', models.CharField(blank=True, max_length=50)),
                ('profession', models.CharField(blank=True, max_length=100)),
                ('pieces', models.IntegerField(blank=True, default=1, null=True, verbose_name='Nombre de pièces souhaitées')),
                ('type', models.CharField(choices=[('locataire', 'Locataire'), ('acheteur', 'Acheteur'), ('proprietaire', 'Propriétaire d\'immeuble')], default='locataire', max_length=20)),
                ('adresse1', models.TextField(default='', verbose_name='Adresse actuelle')),
                ('adresse2', models.TextField(blank=True, null=True, verbose_name='Adresse complémentaire')),
                ('telephone', models.CharField(default='', max_length=20)),
                ('telephone2', models.CharField(blank=True, max_length=20, null=True, verbose_name='Téléphone secondaire')),
                ('mail', models.EmailField(default='', max_length=254)),
                ('piece_identite', models.FileField(blank=True, null=True, upload_to='pieces_identite/%Y/%m/', verbose_name="Pièce d'identité")),
                ('numero_piece_identite', models.CharField(blank=True, max_length=50, null=True, verbose_name="Numéro de pièce d'identité")),
                ('date_validite_piece', models.DateField(blank=True, null=True, verbose_name="Date de validité de la pièce d'identité")),
                ('nom_employeur', models.CharField(blank=True, max_length=100, null=True)),
                ('adresse_employeur', models.TextField(blank=True, null=True)),
                ('telephone_employeur', models.CharField(blank=True, max_length=20, null=True)),
                ('revenu_mensuel', models.DecimalField(blank=True, decimal_places=0, help_text='Montant en XOF', max_digits=12, null=True)),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now)),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='propriete',
            name='proprietaire',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proprietes', to='gestion_immobiliere.tiers'),
        ),
        migrations.RunPython(transfer_locataire_to_tiers),
        migrations.AlterField(
            model_name='location',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gestion_immobiliere.tiers'),
        ),
        migrations.DeleteModel(
            name='Locataire',
        ),
    ]

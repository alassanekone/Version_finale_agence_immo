# Generated by Django 5.1.4 on 2025-04-01 18:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_immobiliere', '0003_location_date_signature_location_prix_vente_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='id_client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gestion_immobiliere.locataire'),
        ),
    ]

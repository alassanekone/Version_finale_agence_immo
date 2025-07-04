# Generated by Django 5.1.4 on 2025-04-06 01:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_immobiliere', '0011_alter_location_options_alter_paiement_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompteBancaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('numero_compte', models.CharField(max_length=50, unique=True)),
                ('solde', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Compte bancaire',
                'verbose_name_plural': 'Comptes bancaires',
            },
        ),
        migrations.CreateModel(
            name='RapportFinancier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_debut', models.DateField()),
                ('date_fin', models.DateField()),
                ('periode', models.CharField(choices=[('jour', 'Journalier'), ('semaine', 'Hebdomadaire'), ('mois', 'Mensuel'), ('trimestre', 'Trimestriel'), ('annee', 'Annuel')], max_length=20)),
                ('total_revenus', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('total_depenses', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('solde_net', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('date_generation', models.DateTimeField(auto_now_add=True)),
                ('commentaires', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Rapport financier',
                'verbose_name_plural': 'Rapports financiers',
                'ordering': ['-date_generation'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_transaction', models.CharField(choices=[('credit', 'Crédit'), ('debit', 'Débit')], max_length=10)),
                ('montant', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date_transaction', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True)),
                ('reference', models.CharField(blank=True, max_length=50, unique=True)),
                ('compte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='gestion_immobiliere.comptebancaire')),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
                'ordering': ['-date_transaction'],
            },
        ),
    ]

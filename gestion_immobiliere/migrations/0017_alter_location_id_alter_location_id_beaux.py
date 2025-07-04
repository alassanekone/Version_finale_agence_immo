# Generated by Django 5.2.1 on 2025-05-15 17:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_immobiliere", "0016_auto_20250508_1559"),
    ]

    operations = [
        migrations.AlterField(
            model_name="location",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="location",
            name="id_beaux",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="gestion_immobiliere.beaux",
            ),
        ),
    ]

# Generated by Django 5.0.6 on 2024-06-20 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacoes', '0010_remove_prova_corrigida'),
    ]

    operations = [
        migrations.AddField(
            model_name='prova',
            name='nota_minima',
            field=models.FloatField(default=0),
        ),
    ]

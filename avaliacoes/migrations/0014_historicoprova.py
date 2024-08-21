# Generated by Django 5.0.6 on 2024-08-12 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacoes', '0013_remove_resposta_prova_realizada'),
        ('materiais', '0016_pasta_area_trilha'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoProva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nota_final', models.FloatField()),
                ('pasta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pasta_name', to='materiais.pasta')),
            ],
        ),
    ]
# Generated by Django 5.0.6 on 2024-06-18 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacoes', '0004_resposta_comentario'),
    ]

    operations = [
        migrations.AddField(
            model_name='prova',
            name='corrigida',
            field=models.BooleanField(default=1),
            preserve_default=False,
        ),
    ]

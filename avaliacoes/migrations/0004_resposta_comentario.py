# Generated by Django 5.0.6 on 2024-06-18 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacoes', '0003_provarealizada'),
    ]

    operations = [
        migrations.AddField(
            model_name='resposta',
            name='comentario',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
# Generated by Django 5.0.6 on 2024-09-02 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacoes', '0023_rename_fk_avaliacao_eficacia_respostaavaliacaoeficacia_avaliacao_eficacia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='respostaavaliacaoeficacia',
            name='avaliacao_eficacia',
        ),
        migrations.DeleteModel(
            name='AvaliacaoEficacia',
        ),
        migrations.DeleteModel(
            name='RespostaAvaliacaoEficacia',
        ),
    ]

# Generated by Django 5.0.6 on 2024-09-02 11:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacoes', '0021_alter_alternativa_texto'),
        ('materiais', '0016_pasta_area_trilha'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AvaliacaoEficacia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avaliado_chefia', models.BooleanField(default=False)),
                ('avaliado_rh', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pasta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='materiais.pasta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RespostaAvaliacaoEficacia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eficacia_qualificacao', models.BooleanField()),
                ('justificativa_qualificacao', models.TextField()),
                ('data_resposta', models.DateTimeField(auto_now_add=True)),
                ('fk_avaliacao_eficacia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.avaliacaoeficacia')),
            ],
        ),
    ]
# Generated by Django 5.0.6 on 2024-08-14 11:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0005_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='VisualizacaoLivro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visualizado_em', models.DateTimeField(auto_now_add=True)),
                ('livro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visualizacoes_livros', to='biblioteca.livro')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visualizacoes_livros', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

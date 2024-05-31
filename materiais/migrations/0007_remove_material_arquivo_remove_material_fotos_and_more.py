# Generated by Django 5.0.4 on 2024-05-31 20:31

import django.db.models.deletion
import materiais.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materiais', '0006_pasta_funcionarios_pasta_setores'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='material',
            name='arquivo',
        ),
        migrations.RemoveField(
            model_name='material',
            name='fotos',
        ),
        migrations.RemoveField(
            model_name='material',
            name='video',
        ),
        migrations.CreateModel(
            name='Arquivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.FileField(upload_to='arquivos/', validators=[materiais.models.validate_file_type])),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='arquivos', to='materiais.material')),
            ],
        ),
        migrations.CreateModel(
            name='Foto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(upload_to='fotos/', validators=[materiais.models.validate_file_type])),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fotos', to='materiais.material')),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='videos/', validators=[materiais.models.validate_file_type])),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='videos', to='materiais.material')),
            ],
        ),
    ]

# Generated by Django 5.0.4 on 2024-06-06 17:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0003_remove_setor_pasta'),
        ('materiais', '0008_remove_foto_material_remove_video_material_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='video_youtube',
            field=models.URLField(default=1),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Visualizacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visualizado_em', models.DateTimeField(auto_now_add=True)),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visualizacoes', to='cadastros.funcionario')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visualizacoes', to='materiais.material')),
                ('pasta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visualizacoes', to='materiais.pasta')),
            ],
        ),
    ]
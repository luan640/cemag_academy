# Generated by Django 5.0.6 on 2024-06-07 08:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0004_areatrilha'),
        ('materiais', '0015_alter_material_video_youtube'),
    ]

    operations = [
        migrations.AddField(
            model_name='pasta',
            name='area_trilha',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pasta_areatrilha', to='cadastros.areatrilha'),
            preserve_default=False,
        ),
    ]
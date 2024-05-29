# Generated by Django 5.0.1 on 2024-05-28 23:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("materiais", "0004_pasta_id_alter_pasta_nome"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="material",
            name="pastas",
        ),
        migrations.AddField(
            model_name="material",
            name="pasta",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pasta_material",
                to="materiais.pasta",
            ),
            preserve_default=False,
        ),
    ]

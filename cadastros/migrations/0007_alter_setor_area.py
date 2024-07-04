# Generated by Django 5.0.6 on 2024-06-10 09:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0006_alter_funcionario_matricula'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setor',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='setor_area', to='cadastros.area'),
        ),
    ]
# Generated by Django 5.0.6 on 2024-08-12 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacoes', '0015_historicoprova_data_realizacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicoprova',
            name='data_realizacao',
            field=models.DateTimeField(),
        ),
    ]

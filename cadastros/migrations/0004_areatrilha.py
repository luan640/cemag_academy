# Generated by Django 5.0.6 on 2024-06-06 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0003_remove_setor_pasta'),
    ]

    operations = [
        migrations.CreateModel(
            name='AreaTrilha',
            fields=[
                ('nome', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
    ]
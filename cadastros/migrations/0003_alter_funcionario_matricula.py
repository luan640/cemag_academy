# Generated by Django 5.0.6 on 2024-10-18 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cadastros', '0002_alter_funcionario_matricula'),
    ]

    operations = [
        migrations.AlterField(
            model_name='funcionario',
            name='matricula',
            field=models.IntegerField(unique=True),
        ),
    ]

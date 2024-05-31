# Generated by Django 4.2.13 on 2024-05-22 22:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('materiais', '0002_alter_material_options_remove_material_pasta_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='material',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='material_user', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='material',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='pasta',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pasta',
            name='created_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='pasta_user', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pasta',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
from django.db import models
from django.core.exceptions import ValidationError
import os
from users.models import CustomUser

def validate_file_type(value):
    ext = os.path.splitext(value.name)[1]  # Obtém a extensão do arquivo
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de arquivo não suportado.')

class Pasta(models.Model):
    nome = models.CharField(max_length=200, primary_key=True)
    descricao = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, related_name='pasta_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class Material(models.Model):
    pastas = models.ManyToManyField(Pasta, related_name='materiais')
    nome = models.CharField(max_length=200)
    descricao = models.TextField(null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True, validators=[validate_file_type])
    arquivo = models.FileField(upload_to='arquivos/', null=True, blank=True, validators=[validate_file_type])
    fotos = models.ImageField(upload_to='fotos/', null=True, blank=True, validators=[validate_file_type])
    created_by = models.ForeignKey(CustomUser, related_name='material_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Materiais"

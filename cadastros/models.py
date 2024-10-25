
from django.db import models
from users.models import CustomUser

class Area(models.Model):

    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):

        return self.nome

class Setor(models.Model):

    area = models.ForeignKey(Area, related_name='setor_area', on_delete=models.CASCADE)
    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):

        return self.nome

class Funcionario(models.Model):
    matricula = models.IntegerField(unique=True)
    nome = models.CharField(max_length=200)
    setor = models.ForeignKey(Setor, related_name='funcionario_setor', on_delete=models.CASCADE) 
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='funcionario', null=True, blank=True)

    def __str__(self):
        return self.nome

    def display_name(self):
        return f"{self.nome} ({self.setor.nome})"

class AreaTrilha(models.Model):

    nome = models.CharField(max_length=100, unique=True)

    def __str__(self):
        
        return self.nome
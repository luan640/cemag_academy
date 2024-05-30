from django.db import models

class Area(models.Model):

    nome = models.CharField(max_length=100, primary_key=True)

    def __str__(self):

        return self.nome

class Setor(models.Model):

    area = models.ForeignKey(Area, related_name='setor_area', on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=100, primary_key=True)

    def __str__(self):

        return self.nome


class Funcionario(models.Model):

    matricula = models.CharField(max_length=200, primary_key=True)
    nome = models.CharField(max_length=200)
    setor = models.ManyToManyField(Setor, related_name='funcionario_setor')

    def __str__(self):
        
        return self.nome
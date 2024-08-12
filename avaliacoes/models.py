from django.db import models
from datetime import datetime

from materiais.models import Pasta
from users.models import CustomUser

import uuid 

class HistoricoProva(models.Model):

    pasta=models.ForeignKey(Pasta, on_delete=models.CASCADE, related_name='pasta_name')
    data_realizacao = models.DateTimeField(default=datetime(2020, 1, 1))
    nota_final = models.FloatField()

class Prova(models.Model):
    
    STATUS = (
        ('ativa', 'Ativa'),
        ('finalizada', 'Finalizada'),
    )

    pasta=models.ForeignKey(Pasta, on_delete=models.CASCADE, related_name='prova_pasta')
    titulo=models.CharField(max_length=200)
    status=models.CharField(max_length=10, choices=STATUS)
    nota_minima=models.FloatField(default=0)
    
class Questao(models.Model):
    
    TIPOS = (
        ('objetiva', 'Objetiva'),
        ('dissertativa', 'Dissertativa'),
    )
    
    prova = models.ForeignKey(Prova, on_delete=models.CASCADE, related_name='questao_prova')
    enunciado = models.TextField()
    tipo = models.CharField(max_length=12, choices=TIPOS)

class Alternativa(models.Model):
    
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name='alternativa_questao')
    texto = models.CharField(max_length=255)
    correta = models.BooleanField(default=False)

class Resposta(models.Model):
    
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name='resposta_questao')
    funcionario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='funcionario_resposta')
    texto = models.TextField(null=True, blank=True)  # Para respostas dissertativas
    alternativa_selecionada = models.ForeignKey(Alternativa, on_delete=models.SET_NULL, null=True, blank=True, related_name='alternativa_alternativa')
    corrigida = models.BooleanField(default=True)
    nota = models.FloatField(null=True, blank=True)
    comentario = models.TextField(null=True, blank=True)  # Para feedback nas respostas dissertativas

class ProvaRealizada(models.Model):
    
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    prova = models.ForeignKey(Prova, on_delete=models.CASCADE)
    data_realizacao = models.DateTimeField(auto_now_add=True)
    identificador_finalizado = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def calcular_nota(self):
        respostas = Resposta.objects.filter(prova_realizada=self)
        nota_total = 0
        for resposta in respostas:
            if resposta.nota:  # Verifica se a nota não é nula (para questões dissertativas ainda não corrigidas)
                nota_total += resposta.nota
        return nota_total
    
    class Meta:
        unique_together = ('usuario', 'prova')
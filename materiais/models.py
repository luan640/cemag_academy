from django.db import models
from django.core.exceptions import ValidationError
import os
import uuid 
from users.models import CustomUser
from cadastros.models import Funcionario,Setor,AreaTrilha

def validate_file_type(value):
    ext = os.path.splitext(value.name)[1]  # Obtém a extensão do arquivo
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi','.csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Tipo de arquivo não suportado.')

class Pasta(models.Model):
    
    nome = models.CharField(max_length=255, unique=True)  # Nome único, mas não chave primária
    descricao = models.TextField(null=True, blank=True)
    setores = models.ManyToManyField(Setor, related_name='pastas_setores', blank=True)
    funcionarios = models.ManyToManyField(Funcionario, related_name='pastas_funcionarios', blank=True)
    area_trilha = models.ForeignKey(AreaTrilha, related_name='pasta_areatrilha', on_delete=models.CASCADE)
    is_norma_regulamentadora = models.BooleanField(default=False)
    pasta_drive = models.CharField(max_length=200, null=True, blank=True)
    carga_horaria = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, related_name='pasta_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

class Material(models.Model):
    
    pasta = models.ForeignKey(Pasta, related_name='pasta_material', on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(null=True, blank=True)
    video_youtube = models.CharField(max_length=200, null=True, blank=True)
    video = models.FileField(upload_to='videos/', null=True, blank=True, validators=[validate_file_type])
    arquivo = models.FileField(upload_to='arquivos/', null=True, blank=True, validators=[validate_file_type])
    fotos = models.ImageField(upload_to='fotos/', null=True, blank=True, validators=[validate_file_type])
    arquivo_drive = models.CharField(max_length=200, null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, related_name='material_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name_plural = "Materiais"

class Visualizacao(models.Model):
    funcionario = models.ForeignKey(Funcionario, related_name='visualizacoes', on_delete=models.CASCADE)
    pasta = models.ForeignKey(Pasta, related_name='visualizacoes', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, related_name='visualizacoes', on_delete=models.CASCADE)
    visualizado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.funcionario} visualizou {self.material} em {self.visualizado_em}'

class AvaliacaoEficacia(models.Model):
    pasta = models.ForeignKey(Pasta, on_delete=models.CASCADE)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    avaliado_chefia = models.BooleanField(default=False)
    avaliado_rh = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação Eficácia {self.pasta.nome} - {self.usuario.first_name} {self.usuario.last_name} "

class RespostaAvaliacaoEficacia(models.Model):
    avaliacao_eficacia = models.ForeignKey(AvaliacaoEficacia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=0)
    eficacia_qualificacao = models.BooleanField()
    justificativa_qualificacao = models.TextField()
    data_resposta = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resposta Avaliação - {self.usuario.first_name} p/ {self.avaliacao_eficacia.usuario.first_name}"
    
class Certificado(models.Model):
    pasta = models.ForeignKey(Pasta, on_delete=models.CASCADE)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    identificador_finalizado = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    data_emissao_certificado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificado da {self.usuario.first_name} referente a {self.pasta.nome} - {self.identificador_finalizado}"

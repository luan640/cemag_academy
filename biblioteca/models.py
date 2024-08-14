from django.db import models
from users.models import CustomUser
from cadastros.models import Funcionario

from materiais.models import validate_file_type

class Livro(models.Model):
    
    titulo = models.CharField(max_length=255)
    autor = models.CharField(max_length=255)
    arquivo_pdf = models.FileField(upload_to='livros/', validators=[validate_file_type])
    capa = models.ImageField(upload_to='capa/', null=True, blank=True, validators=[validate_file_type])
    ano = models.PositiveIntegerField()
    idioma = models.CharField(max_length=50)
    created_by = models.ForeignKey(CustomUser, related_name='livro_user', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.titulo

class Rating(models.Model):
    user = models.ForeignKey(CustomUser, related_name='ratings', on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, related_name='ratings', on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.livro} - {self.score}"

class VisualizacaoLivro(models.Model):
    user = models.ForeignKey(CustomUser, related_name='visualizacoes_livros', on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, related_name='visualizacoes_livros', on_delete=models.CASCADE)
    visualizado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} visualizou {self.livro} em {self.visualizado_em}'

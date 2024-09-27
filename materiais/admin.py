from django.contrib import admin
from .models import Pasta, Material, Visualizacao, AvaliacaoEficacia, RespostaAvaliacaoEficacia,Certificado

admin.site.register(Pasta)
admin.site.register(Material)
admin.site.register(Visualizacao)
admin.site.register(AvaliacaoEficacia)
admin.site.register(RespostaAvaliacaoEficacia)
admin.site.register(Certificado)
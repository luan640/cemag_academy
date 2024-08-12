from django.contrib import admin

from .models import Prova,Questao,Resposta,Alternativa,ProvaRealizada

admin.site.register(Prova)
admin.site.register(Questao)
admin.site.register(Resposta)
admin.site.register(Alternativa)
admin.site.register(ProvaRealizada)


from django.contrib import admin
from core.admin import RestrictedAdmin

from .models import Prova,Questao,Resposta,Alternativa,ProvaRealizada

admin.site.register(Prova,RestrictedAdmin)
admin.site.register(Questao,RestrictedAdmin)
admin.site.register(Resposta,RestrictedAdmin)
admin.site.register(Alternativa,RestrictedAdmin)
admin.site.register(ProvaRealizada,RestrictedAdmin)


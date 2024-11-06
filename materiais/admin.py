from django.contrib import admin
from core.admin import RestrictedAdmin
from .models import Pasta, Material, Visualizacao, AvaliacaoEficacia, RespostaAvaliacaoEficacia,Certificado
    
admin.site.register(Pasta,RestrictedAdmin)
admin.site.register(Material,RestrictedAdmin)
admin.site.register(Visualizacao,RestrictedAdmin)
admin.site.register(AvaliacaoEficacia,RestrictedAdmin)
admin.site.register(RespostaAvaliacaoEficacia,RestrictedAdmin)
admin.site.register(Certificado,RestrictedAdmin)


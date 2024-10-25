from django.contrib import admin
from .models import Funcionario, Area, Setor, AreaTrilha

# Adicione filtros específicos para cada modelo

class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'setor')  # Campos exibidos na lista de funcionários
    list_filter = ('setor',)  # Filtro para o campo setor
    search_fields = ('nome', 'matricula')  # Pesquisa por nome e matrícula

class AreaAdmin(admin.ModelAdmin):
    list_display = ('nome',)  # Exibir nome na lista de áreas
    search_fields = ('nome',)  # Pesquisa por nome

class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'area')  # Campos exibidos na lista de setores
    list_filter = ('area',)  # Filtro para o campo área
    search_fields = ('nome',)  # Pesquisa por nome de setor

class AreaTrilhaAdmin(admin.ModelAdmin):
    list_display = ('nome',)  # Exibir nome na lista de áreas de trilha
    search_fields = ('nome',)  # Pesquisa por nome

# Registrar as classes personalizadas no admin
admin.site.register(Funcionario, FuncionarioAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Setor, SetorAdmin)
admin.site.register(AreaTrilha, AreaTrilhaAdmin)

from django.contrib import admin

from .models import Funcionario,Area,Setor,AreaTrilha


admin.site.register(Funcionario)
admin.site.register(Area)
admin.site.register(Setor)
admin.site.register(AreaTrilha)
from django.contrib import admin
from .models import Pasta, Material

class MaterialInline(admin.TabularInline):
    model = Material.pastas.through
    extra = 1

class PastaAdmin(admin.ModelAdmin):
    inlines = [MaterialInline]

class MaterialAdmin(admin.ModelAdmin):
    filter_horizontal = ('pastas',)

admin.site.register(Pasta, PastaAdmin)
admin.site.register(Material, MaterialAdmin)
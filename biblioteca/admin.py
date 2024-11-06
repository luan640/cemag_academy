from django.contrib import admin
from .models import Livro
from core.admin import RestrictedAdmin

admin.site.register(Livro,RestrictedAdmin)
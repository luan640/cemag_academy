from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['matricula', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('matricula', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'setores')}),  # Adicionando 'setores' aos campos de permissões
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('matricula', 'password1', 'password2', 'is_staff', 'is_active', 'setores')}  # Adicionando 'setores' aos campos para adicionar usuário
        ),
    )
    search_fields = ('matricula',)
    ordering = ('matricula',)
    filter_horizontal = ('setores',)  # Adicionando o filtro horizontal para o campo 'setores'

admin.site.register(CustomUser, CustomUserAdmin)
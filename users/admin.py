from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['matricula', 'first_name', 'last_name', 'email','type','is_active', 'is_staff']
    list_filter = ['is_active', 'is_staff', 'type']
    fieldsets = (
        (None, {'fields': ('matricula', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('matricula', 'password1', 'password2', 'first_name', 'last_name', 'email', 'type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )
    search_fields = ('matricula',)
    ordering = ('matricula',)

admin.site.register(CustomUser, CustomUserAdmin)
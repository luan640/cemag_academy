from django.contrib import admin

class RestrictedAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Permite acesso a todos os admins para o usuário com matrícula 9999
        return request.user.is_authenticated and request.user.matricula == 9999

    def has_view_permission(self, request, obj=None):
        # Permite a visualização dos dados
        return request.user.is_authenticated and request.user.matricula == 9999

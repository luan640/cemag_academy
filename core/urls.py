from django.urls import path

from . import views
# from .views import trilhas_por_setor_api,assiduidade_por_setor_api

urlpatterns = [
    path('', views.painel_home, name='home'),
    path('administrador', views.painel_home_superuser, name='painel_home_superuser'),  # Adicione esta linha
    # path('api/trilhas_por_setor', trilhas_por_setor_api, name='trilhas_por_setor_api'),
    # path('api/assiduidade_por_setor', assiduidade_por_setor_api, name='assiduidade_por_setor_api')
]
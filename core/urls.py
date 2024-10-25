from django.urls import path

from . import views
# from .views import trilhas_por_setor_api,assiduidade_por_setor_api

urlpatterns = [
    path('', views.painel_home, name='home'),
    path('administrador', views.painel_home_superuser, name='painel_home_superuser'),  # Adicione esta linha
    path('load_trilhas_finalizadas', views.load_trilhas_finalizadas, name='load_trilhas_finalizadas'),  # Adicione esta linha
    path('load_progresso_geral_individual', views.load_progresso_geral_individual, name='load_progresso_geral_individual'),  # Adicione esta linha
    path('load_progresso_funcionarios', views.load_progresso_funcionarios, name='load_progresso_funcionarios'),  # Adicione esta linha
    path('ultimas_trilhas', views.ultimas_trilhas, name='ultimas_trilhas'),  # Adicione esta linha
    path('ultimos_acessos', views.ultimos_acessos, name='ultimos_acessos'),  # Adicione esta linha
    # path('api/trilhas_por_setor', trilhas_por_setor_api, name='trilhas_por_setor_api'),
    # path('api/assiduidade_por_setor', assiduidade_por_setor_api, name='assiduidade_por_setor_api')
]
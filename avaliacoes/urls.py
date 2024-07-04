from django.urls import path

from . import views

urlpatterns = [

    path('<int:pk>/criar-prova/', views.criar_prova, name='criar-prova'),
    path('<int:pk>/salvar-prova/', views.salvar_prova, name='salvar-prova'),
    path('<int:pk>/realizar-prova/', views.realizar_prova, name='realizar-prova'),
    path('<int:pk>/list-provas/', views.list_prova, name='list-prova'),
    path('<int:pk_prova>/<int:pk_user>/corrigir-prova/', views.corrigir_questoes_dissertativas, name='corrigir-prova'),

]
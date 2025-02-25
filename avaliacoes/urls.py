from django.urls import path

from . import views

urlpatterns = [

    path('<int:pk>/criar-prova/', views.criar_prova, name='criar-prova'),
    path('<int:pk>/salvar-prova/', views.salvar_prova, name='salvar-prova'),
    path('<int:pk>/deletar-prova/', views.delete_prova, name='deletar-prova'),
    path('<int:pk>/realizar-prova/', views.realizar_prova, name='realizar-prova'),
    path('<int:pk>/list-provas/', views.list_prova, name='list-prova'),
    path('<int:pk>/visualizar-prova/<int:pk_matricula>/', views.visualizar_prova, name='visualizar-prova'),
    path('<int:pk>/editar-prova/', views.editar_prova, name='editar-prova'),
    path('<int:pk_questoes>/editar-questoes-alternativas/', views.editar_questoes_alternativas, name='editar-questoes-alternativas'),
    path('<int:pk_prova>/<int:pk_user>/corrigir-prova/', views.corrigir_questoes_dissertativas, name='corrigir-prova'),
    path('<int:pk_prova>/<int:pk_user>/refazer-prova/', views.refazer_prova, name='refazer-prova')

]
from django.urls import path

from . import views

urlpatterns = [
    path('funcionario', views.funcionario_cadastro, name='funcionarios'),
    path('funcionario/<int:pk>/edit', views.funcionario_edit, name='edit-funcionario'),
    path('funcionario/<int:pk>/delete', views.funcionario_delete, name='delete-funcionario'),
    path('funcionarios/importar/', views.importar_funcionarios, name='importar-funcionarios'),

    path('setor', views.setor_cadastro, name='setores'),
    path('setor/<int:pk>/edit', views.setor_edit, name='edit-setor'),
    path('setor/<int:pk>/delete', views.setor_delete, name='delete-setor'),

    path('area', views.area_cadastro, name='areas'),
    path('area/<int:pk>/edit', views.area_edit, name='edit-area'),
    path('area/<int:pk>/delete', views.area_delete, name='delete-area'),

]
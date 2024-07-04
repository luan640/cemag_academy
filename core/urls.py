from django.urls import path

from . import views

urlpatterns = [
    path('', views.painel_home, name='home'),
    path('administrador', views.painel_home_superuser, name='painel_home_superuser'),  # Adicione esta linha

]
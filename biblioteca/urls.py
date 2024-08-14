from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('livros/', views.list_livro, name='list-livro'),
    path('livros/add', views.livro_add, name='add-livro'),
    path('livros/add-rating/', views.add_rating, name='add-rating'),
    path('livros/registrar-visualizacao-livro', views.registrar_visualizacao_livro, name='registrar_visualizacao_livro'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
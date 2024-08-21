from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path('pasta/', views.pastas_list, name='list-pasta'),
    path('pasta/<int:pk>/detail', views.pastas_detail, name='detail-pasta'),
    path('pasta/add/', views.pastas_add, name='add-pasta'),
    path('pasta/<int:pk>/edit', views.pasta_edit, name='edit-pasta'),
    path('pasta/<int:pk>/delete/', views.pasta_delete, name='delete-pasta'),
    path('pasta/<int:pk>/frequencia/', views.gerar_ficha_frequencia, name='frequencia-pasta'),
    path('pasta/<int:pk>/participantes/', views.list_participantes, name='list-participantes'),
    path('pasta/<int:pk>/<int:pk_pasta>/certificado/', views.gerar_certificado, name='gerar-certificado'),
    
    path('material/', views.material_list, name='list-material'),
    path('material/<int:pk>/detail', views.material_detail, name='detail-material'),
    path('material/add/<int:pk>/', views.material_add_in_pasta, name='add-material'),
    path('material/<int:pk_material>/edit/<int:pk_pasta>/', views.material_edit, name='edit-material'),
    path('material/<int:pk_material>/delete/<int:pk_pasta>/', views.material_delete, name='delete-material'),
    path('material/registrar-visualizacao/', views.registrar_visualizacao, name='registrar_visualizacao'),

    path('jornada/detail/', views.jornada_detail, name='jornada_detail'),
    path('jornada/detail/<int:pk_user>', views.jornada_detail, name='jornada_detail_unique'),

    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
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
    
    path('material/', views.material_list, name='list-material'),
    path('material/<int:pk>/detail', views.material_detail, name='detail-material'),
    path('material/add/', views.material_add, name='add-material'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
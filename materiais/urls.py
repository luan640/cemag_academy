from django.urls import path

from . import views

urlpatterns = [
    path('pasta/', views.pastas_list, name='list-pastas'),
    path('pasta/<str:pk>', views.pastas_detail, name='detail-pasta'),
    path('pasta/add/', views.pastas_add, name='add-pasta'),
    # path('<int:pk>/edit/', views.pasta_edit, name='edit'),
    # path('<int:pk>/delete/', views.pasta_delete, name='delete'),
]
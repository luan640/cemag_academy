from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from . import views, views_drive

urlpatterns = [
    path('pasta/', views.pastas_list, name='list-pasta'),
    path('pasta/creators/', views.pastas_creators, name='pastas-creators'),
    path('pasta/<int:pk>/detail/', views.pastas_detail, name='detail-pasta'),
    # Drive (lista completa) - usado na edição da pasta
    path('pasta/<int:pk>/drive/', views.pastas_detail_drive, name='pastas-detail-drive'),
    # Drive filtrado pelos arquivos escolhidos - usado na tela de detalhes
    path('pasta/<int:pk>/drive-filtrado/', views_drive.pastas_detail_drive_filtrado, name='pastas-detail-drive-filtrado'),
    path('drive/download/<str:file_id>/', views.download_drive_file, name='download_drive_file'),
    path('drive/export-google-file/<str:file_id>/', views.export_google_file, name='export_google_file'),
    path('drive/export/<str:file_id>/', views.export_drive_sheet, name='drive_export_sheet'),
    path('drive/clear/<str:pk>/', views.limpar_cache_pasta_drive, name='limpar_cache_drive'),
    path('drive/metadata/<str:file_id>/', views.get_drive_file_metadata, name='get_drive_file_metadata'),
    
    path('pasta/add/', views.pastas_add, name='add-pasta'),
    path('pasta/<int:pk>/edit/', views_drive.pasta_edit_drive, name='edit-pasta'),
    path('pasta/<int:pk>/delete/', views.pasta_delete, name='delete-pasta'),
    path('pasta/<int:pk>/frequencia/', views.gerar_ficha_frequencia, name='frequencia-pasta'),
    path('pasta/<int:pk>/participantes/', views.list_participantes, name='list-participantes'),
    
    path('pasta/certificado/', views.gerar_certificado, name='gerar-certificado'),
    path('pasta/<int:pk>/funcionarios-avaliaram',views.funcionarios_avaliaram,name='funcionarios_avaliaram'),

    path('consultar/certificado/<str:uuid>/', views.consultar_certificado, name='consultar_certificado'),
    path('consultar/certificado/',login_required(TemplateView.as_view(template_name='certificados/consultar_certificados.html')),name='consultar_certificados'),
    
    path('material/', views.material_list, name='list-material'),
    path('material/<int:pk>/detail', views.material_detail, name='detail-material'),
    path('material/add/<int:pk>/', views.material_add_in_pasta, name='add-material'),
    path('material/<int:pk_material>/edit/<int:pk_pasta>/', views.material_edit, name='edit-material'),
    path('material/<int:pk_material>/delete/<int:pk_pasta>/', views.material_delete, name='delete-material'),
    path('material/registrar-visualizacao/', views.registrar_visualizacao, name='registrar_visualizacao'),
    
    path('avaliacao/colaborador/<int:pk>', views.avaliacao, name='avaliacao'),
    path('avaliacao/supervisor/<int:pk>/', views.avaliacao_chefia, name='avaliacao_chefia'),
    path('avaliacao/respostas-avaliacao/<int:pk_avaliacao>/', views.respostas_avaliacao, name='respostas-avaliacao'),

    path('jornada/detail/', views.jornada_detail, name='jornada_detail'),
    path('jornada/detail/<int:matricula>', views.jornada_detail_unique, name='jornada_detail_unique'),

    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

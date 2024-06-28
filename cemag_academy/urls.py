from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('materiais/', include('materiais.urls')),
    path('cadastro/', include('cadastros.urls')),
    path('home/', include('core.urls')),
    path('avaliacao/', include('avaliacoes.urls')),
    path('biblioteca/', include('biblioteca.urls')),
    path('', include('users.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

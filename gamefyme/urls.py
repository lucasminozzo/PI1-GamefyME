from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('atividades/', include(('atividades.urls', 'atividades'), namespace='atividades')),
    path('relatorios/', include('relatorios.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
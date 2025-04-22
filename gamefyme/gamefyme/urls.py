from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('core.urls', 'core'), namespace='core')),
    path('auth/', include(('usuarios.urls', 'usuarios'), namespace='auth')),
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('atividades/', include(('atividades.urls', 'atividades'), namespace='atividades')),
]
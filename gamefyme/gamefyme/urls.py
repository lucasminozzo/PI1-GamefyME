from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(('usuarios.urls', 'usuarios'), namespace='auth')),
    path('usuarios/', include(('usuarios.urls', 'usuarios'), namespace='usuarios')),
    path('', include(('core.urls', 'core'), namespace='core')),
]
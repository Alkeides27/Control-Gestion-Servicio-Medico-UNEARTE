"""
URL configuration for sistema_medico project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from types import MethodType

def has_admin_permission(self, request):
    """
    Custom permission check for the admin site.
    Allows access only to active staff members with the 'admin' role
    or to superusers.
    """
    if not request.user.is_active or not request.user.is_staff:
        return False
    
    # Superusers always have access
    if request.user.is_superuser:
        return True
    
    # Custom role check for other staff members
    if hasattr(request.user, 'perfilusuario') and request.user.perfilusuario.rol == 'admin':
        return True
        
    # Deny access otherwise
    return False

# Monkey-patch the has_permission method of the default admin site
admin.site.has_permission = MethodType(has_admin_permission, admin.site)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('pacientes/', include('pacientes.urls', namespace='pacientes')),
    path('citas/', include('citas.urls', namespace='citas')),
    path('historiales/', include('historiales.urls', namespace='historiales')),
    path('inventario/', include('inventario.urls', namespace='inventario')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Servir archivos estáticos y multimedia durante el desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('acceso-denegado/', views.AccesoDenegadoView.as_view(), name='acceso_denegado'),
    path('search/', views.search_all, name='search_all'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('usuarios/', views.UsuarioListView.as_view(), name='lista_usuarios'),
    path('usuarios/crear/', views.UsuarioCreateView.as_view(), name='crear_usuario'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='eliminar_usuario'),
    path('usuarios/<int:pk>/cambiar-contrasena/', views.UsuarioSetPasswordView.as_view(), name='cambiar_contrasena'),
    path('usuarios/<int:user_id>/cambiar-rol/', views.cambiar_rol, name='cambiar_rol'),
    path('perfil/', views.PerfilView.as_view(), name='perfil'),
]
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registro, dashboard, registrar_asistencia

urlpatterns = [
    path('registro/', registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('asistencia/', registrar_asistencia, name='registrar_asistencia'),
]

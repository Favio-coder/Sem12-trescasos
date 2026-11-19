from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path,include
from .views import home,dashboard
urlpatterns=[path('admin/',admin.site.urls),path('',home,name='home'),path('dashboard/',dashboard,name='dashboard'),path('accounts/login/',auth_views.LoginView.as_view(template_name='registration/login.html'),name='login'),path('accounts/logout/',auth_views.LogoutView.as_view(),name='logout'),path('empleados/',include('empleados.urls')),path('asistencias/',include('asistencias.urls')),path('permisos/',include('permisos.urls'))]

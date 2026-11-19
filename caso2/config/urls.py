from django.contrib import admin
from django.urls import path, include
from usuarios.views import home, dashboard, historial
urlpatterns=[path('admin/',admin.site.urls),path('',home,name='home'),path('dashboard/',dashboard,name='dashboard'),path('historial/<int:pk>/',historial,name='historial'),path('accounts/',include('django.contrib.auth.urls')),path('citas/',include('citas.urls'))]

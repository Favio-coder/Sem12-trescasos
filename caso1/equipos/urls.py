from django.urls import path
from . import views
urlpatterns=[path('',views.catalogo,name='catalogo'),path('dashboard/',views.dashboard,name='dashboard'),path('prestamos/nuevo/',views.solicitar,name='solicitar'),path('prestamos/<int:pk>/devolver/',views.devolver,name='devolver'),path('auditoria/',views.auditoria,name='auditoria')]

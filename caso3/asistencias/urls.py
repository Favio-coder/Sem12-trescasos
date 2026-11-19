from django.urls import path
from .views import marcar,historial,exportar
urlpatterns=[path('marcar/<str:accion>/',marcar,name='marcar'),path('',historial,name='asistencias'),path('exportar/',exportar,name='exportar')]

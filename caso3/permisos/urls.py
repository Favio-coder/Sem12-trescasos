from django.urls import path
from .views import solicitar,mis_permisos,resolver
urlpatterns=[path('solicitar/',solicitar,name='solicitar_permiso'),path('',mis_permisos,name='mis_permisos'),path('<int:pk>/<str:estado>/',resolver,name='resolver_permiso')]

from django.urls import path
from .views import crear, cancelar, disponibilidad, registrar_consulta, agregar_nota
urlpatterns=[
    path('nueva/',crear,name='cita_nueva'),
    path('<int:pk>/cancelar/',cancelar,name='cita_cancelar'),
    path('disponibilidad/',disponibilidad,name='disponibilidad'),
    path('<int:pk>/consulta/',registrar_consulta,name='registrar_consulta'),
    path('consulta/<int:pk>/nota/',agregar_nota,name='agregar_nota'),
]

from django.contrib import admin
from .models import Auditoria,Notificacion
@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin): list_display=('fecha_hora','usuario','accion','recurso','registro_id','ip');list_filter=('accion','fecha_hora');search_fields=('usuario__username','recurso','descripcion');readonly_fields=('usuario','accion','recurso','registro_id','fecha_hora','ip','descripcion')
admin.site.register(Notificacion)

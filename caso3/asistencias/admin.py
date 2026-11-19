from django.contrib import admin
from .models import Asistencia,CorreccionAsistencia
@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin): list_display=('empleado','fecha','hora_entrada','hora_salida','horas_trabajadas','horas_extras','estado');list_filter=('estado','fecha','empleado__area');search_fields=('empleado__dni','empleado__nombres','empleado__apellidos');readonly_fields=('horas_trabajadas','horas_extras','creado','actualizado')
@admin.register(CorreccionAsistencia)
class CorreccionAdmin(admin.ModelAdmin): list_display=('asistencia','responsable','motivo','fecha_hora');readonly_fields=('fecha_hora','valores_anteriores','valores_nuevos')

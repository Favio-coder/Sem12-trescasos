from django.contrib import admin
from .models import Area,Empleado
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin): list_display=('nombre','jefe','activa','hora_entrada','hora_salida');list_filter=('activa',);search_fields=('nombre',)
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin): list_display=('dni','nombre_completo','cargo','area','antiguedad','activo');list_filter=('area','cargo','activo','tipo_contrato');search_fields=('dni','nombres','apellidos','correo');readonly_fields=('antiguedad',)

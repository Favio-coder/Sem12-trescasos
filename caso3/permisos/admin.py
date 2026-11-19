from django.contrib import admin,messages
from django.core.exceptions import ValidationError
from .models import Permiso
@admin.action(description='Aprobar permisos seleccionados')
def aprobar(modeladmin,request,queryset):
    ok=0
    for p in queryset:
        try:p.resolver(request.user,'aprobado');ok+=1
        except ValidationError as e:modeladmin.message_user(request,f'Solicitud #{p.pk}: {e.messages[0]}',level=messages.ERROR)
    modeladmin.message_user(request,f'{ok} solicitud(es) aprobada(s).')
@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin): list_display=('empleado','tipo','fecha_inicio','fecha_fin','estado','aprobador');list_filter=('tipo','estado','fecha_inicio');search_fields=('empleado__dni','empleado__nombres');readonly_fields=('aprobador','fecha_aprobacion','creado');actions=[aprobar]

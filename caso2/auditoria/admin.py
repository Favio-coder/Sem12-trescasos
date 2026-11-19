from django.contrib import admin
from .models import AuditoriaMedica
@admin.register(AuditoriaMedica)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display=('fecha_hora','usuario','accion','recurso','resultado','ip'); list_filter=('resultado','accion','fecha_hora'); readonly_fields=('usuario','paciente','recurso','accion','fecha_hora','ip','resultado');
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False

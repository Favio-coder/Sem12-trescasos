from django.contrib import admin
from .models import Cita,ConsultaMedica,NotaConsulta
@admin.action(description='Marcar citas seleccionadas como completadas')
def completar(modeladmin,request,queryset):
    if request.user.has_perm('citas.change_cita'): queryset.filter(estado='programada').update(estado='completada')
@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display=('fecha','hora','paciente','medico','especialidad','estado'); list_filter=('fecha','medico','especialidad','estado'); search_fields=('paciente__dni','paciente__nombres','paciente__apellidos'); list_select_related=('paciente','medico','especialidad'); actions=[completar]
admin.site.register(ConsultaMedica)
admin.site.register(NotaConsulta)

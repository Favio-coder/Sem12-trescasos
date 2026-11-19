from django.contrib import admin
from .models import Medico,Especialidad,HorarioMedico
@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display=('nombres','apellidos','cmp','especialidad','consultorio','activo','total_consultas'); list_filter=('especialidad','activo'); search_fields=('nombres','apellidos','cmp'); list_select_related=('especialidad',)
    def total_consultas(self,obj): return obj.consultas.count()
admin.site.register(Especialidad)
admin.site.register(HorarioMedico)

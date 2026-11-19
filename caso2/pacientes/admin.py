from django.contrib import admin
from .models import Paciente
@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display=('dni','nombres','apellidos','tipo','edad','ultima_consulta'); search_fields=('dni','nombres','apellidos'); list_filter=('tipo',); readonly_fields=('fecha_registro',)
    def edad(self,obj):
        from datetime import date
        h=date.today(); return h.year-obj.fecha_nacimiento.year-((h.month,h.day)<(obj.fecha_nacimiento.month,obj.fecha_nacimiento.day))
    edad.short_description='Edad'
    def ultima_consulta(self,obj): return obj.consultas.order_by('-atendida_en').values_list('atendida_en',flat=True).first()

from django.contrib import admin, messages
from django.utils.html import format_html
from django.core.mail import mail_admins
from .models import Equipo, Prestamo, Categoria, Laboratorio, Auditoria
@admin.action(description='Marcar equipos seleccionados en mantenimiento')
def mantenimiento(modeladmin,request,queryset): queryset.update(estado=Equipo.Estado.MANTENIMIENTO)
@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display=('codigo_patrimonial','nombre','categoria','laboratorio','estado_color','stock_total','stock_disponible','dias_mantenimiento')
    list_filter=('laboratorio','estado','categoria'); search_fields=('codigo_patrimonial','nombre','categoria__nombre'); readonly_fields=('fecha_registro',)
    actions=[mantenimiento]; list_select_related=('categoria','laboratorio')
    @admin.display(description='Estado')
    def estado_color(self,obj):
        color={'operativo':'green','mantenimiento':'#c47a00','baja':'red'}.get(obj.estado,'gray'); return format_html('<b style="color:{}">{}</b>',color,obj.get_estado_display())
    @admin.display(description='Días desde mantenimiento')
    def dias_mantenimiento(self,obj): return obj.dias_desde_mantenimiento if obj.dias_desde_mantenimiento is not None else 'Sin registro'
@admin.action(description='Enviar recordatorios de devolución')
def recordatorios(modeladmin,request,queryset):
    for p in queryset.select_related('docente','equipo'):
        if p.docente.email: mail_admins('Recordatorio de devolución',f'{p.docente.get_username()}: devolver {p.equipo}',fail_silently=True)
    modeladmin.message_user(request,'Recordatorios procesados mediante el backend de correo configurado.',messages.SUCCESS)
@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display=('docente','equipo','cantidad','fecha_prestamo','fecha_prevista_devolucion','fecha_real_devolucion','estado','dias_retraso')
    list_filter=('estado','fecha_prestamo','fecha_prevista_devolucion','docente'); search_fields=('equipo__codigo_patrimonial','docente__username','docente__first_name','docente__last_name'); list_select_related=('docente','equipo'); actions=[recordatorios]
    @admin.display(description='Días de retraso')
    def dias_retraso(self,obj): return obj.dias_retraso
admin.site.register((Categoria,Laboratorio,Auditoria))

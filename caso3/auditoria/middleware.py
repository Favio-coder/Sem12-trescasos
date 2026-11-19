from datetime import time, timedelta
from django.contrib import messages
from django.utils import timezone
from auditoria.models import Auditoria
from asistencias.models import Asistencia

class CuentaActivaMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        if request.user.is_authenticated and not request.user.is_active:
            from django.contrib.auth import logout
            logout(request)
        return self.get_response(request)

class RecordatorioAsistenciaMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        response=self.get_response(request)
        if request.user.is_authenticated and not request.session.get('attendance_reminder_checked'):
            request.session['attendance_reminder_checked']=True
            try:
                emp=request.user.empleado; today=timezone.localdate()
                if today.weekday()<5 and not Asistencia.objects.filter(empleado=emp,fecha=today,hora_entrada__isnull=False).exists():
                    messages.info(request,'Recuerda marcar tu entrada de hoy.')
            except Exception: pass
        return response

class AuditoriaMiddleware:
    METHODS={'POST','PUT','PATCH','DELETE'}
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        response=self.get_response(request)
        if request.method in self.METHODS and request.user.is_authenticated and response.status_code<400:
            path=request.path_info
            if any(x in path for x in ('asistencia','permiso','correccion','admin')):
                ip=request.META.get('HTTP_X_FORWARDED_FOR','').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
                Auditoria.objects.create(usuario=request.user,accion=request.method,recurso=path[:100],registro_id='',ip=ip,descripcion='Operación web completada')
        return response

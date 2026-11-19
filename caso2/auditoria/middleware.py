from django.contrib import messages
from django.utils import timezone
from auditoria.models import AuditoriaMedica
class AuditMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        response=self.get_response(request)
        if request.path.startswith('/historial/'):
            user=request.user if request.user.is_authenticated else None
            try: pid=int(request.path.strip('/').split('/')[-1])
            except (ValueError,IndexError): pid=None
            paciente_id=getattr(getattr(user,'perfil_paciente',None),'pk',None)
            medico=getattr(user,'perfil_medico',None) if user else None
            allowed=bool(user and user.is_authenticated and (
                user.is_superuser or paciente_id==pid or
                (medico and user.has_perm('pacientes.ver_historial_clinico'))
            ) and response.status_code < 400)
            ip=request.META.get('HTTP_X_FORWARDED_FOR','').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
            from pacientes.models import Paciente
            AuditoriaMedica.objects.create(usuario=user,paciente=Paciente.objects.filter(pk=pid).first(),recurso='historial',accion='consulta',ip=ip or None,resultado='autorizado' if allowed else 'denegado')
        return response
class ClinicalHoursMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request): return self.get_response(request)
class DoctorAlertMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        response=self.get_response(request)
        if request.user.is_authenticated and request.path=='/dashboard/' and hasattr(request.user,'perfil_medico') and not request.session.get('doctor_alerted'):
            from citas.models import Cita
            count=Cita.objects.filter(medico=request.user.perfil_medico,fecha=timezone.localdate(),estado='programada').count()
            if count: messages.info(request,f'Tiene {count} cita(s) pendiente(s) hoy.')
            request.session['doctor_alerted']=True
        return response

from django.utils import timezone
from .models import Auditoria, Prestamo

class AuditoriaMiddleware:
    def __init__(self,get_response): self.get_response=get_response
    def __call__(self,request):
        user=getattr(request,'user',None)
        if user and user.is_authenticated and user.groups.filter(name='Docente').exists():
            request.prestamos_vencidos=Prestamo.objects.filter(docente=user,estado__in=['activo','vencido'],fecha_prevista_devolucion__lt=timezone.localdate()).count()
        else: request.prestamos_vencidos=0
        response=self.get_response(request)
        path=request.path
        if request.method=='POST' and any(x in path for x in ('prestamo','devolucion','delete','eliminar')) and user and user.is_authenticated:
            ip=request.META.get('HTTP_X_FORWARDED_FOR','').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
            Auditoria.objects.create(usuario=user,accion='operacion',direccion_ip=ip or None,recurso=path[:120],descripcion=f'{request.method} {path}')
        return response

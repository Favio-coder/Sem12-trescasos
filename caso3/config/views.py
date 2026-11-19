from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from empleados.models import Empleado,Area
from asistencias.models import Asistencia
from permisos.models import Permiso

def home(request): return render(request,'home.html')
@login_required
def dashboard(request):
    user=request.user; today=timezone.localdate(); group=user.groups.values_list('name',flat=True).first()
    context={'grupo':group,'hoy':today,'notificaciones':user.notificaciones.filter(leida=False) if hasattr(user,'notificaciones') else []}
    try: context['empleado']=user.empleado;context['asistencia_hoy']=Asistencia.objects.filter(empleado=user.empleado,fecha=today).first()
    except Exception: pass
    if 'empleado' in context:
        used=sum(p.dias for p in Permiso.objects.filter(empleado=context['empleado'],tipo='vacaciones',estado='aprobado'))
        context['saldo_vacaciones']=max(0,30-used)
    if user.is_superuser or group=='Administrador RRHH':
        context.update(total=Empleado.objects.count(),activos=Empleado.objects.filter(activo=True).count(),asistencias=Asistencia.objects.filter(fecha=today).count(),pendientes=Permiso.objects.filter(estado='pendiente').count(),extras=Asistencia.objects.aggregate(x=__import__('django.db.models').db.models.Sum('horas_extras'))['x'] or 0,areas=Area.objects.all())
    elif group=='Jefe de Área':
        context['equipo']=Empleado.objects.filter(area__jefe=user);context['pendientes_lista']=Permiso.objects.filter(empleado__area__jefe=user,estado='pendiente')
    return render(request,'dashboard/index.html',context)

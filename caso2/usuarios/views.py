from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils import timezone
from pacientes.models import Paciente
from medicos.models import Medico,Especialidad
from citas.models import Cita

def home(request): return render(request,'home.html',{'especialidades':Especialidad.objects.filter(activa=True)})
@login_required
def dashboard(request):
    u=request.user
    ctx={'pacientes':Paciente.objects.count(),'medicos':Medico.objects.filter(activo=True).count(),'citas':Cita.objects.filter(estado='programada').count(),'especialidades':Especialidad.objects.all()}
    if u.is_staff:
        ctx['agenda']=Cita.objects.filter(fecha=timezone.localdate()).select_related('paciente','medico')
        ctx['counts']={'Completadas':Cita.objects.filter(estado='completada').count(),'Canceladas':Cita.objects.filter(estado='cancelada').count()}
    elif hasattr(u,'perfil_medico'): ctx['agenda']=Cita.objects.filter(medico=u.perfil_medico,fecha__gte=timezone.localdate()).select_related('paciente').order_by('fecha','hora')
    elif hasattr(u,'perfil_paciente'): ctx['agenda']=Cita.objects.filter(paciente=u.perfil_paciente).select_related('medico','especialidad').order_by('-fecha')
    else: ctx['agenda']=Cita.objects.filter(fecha=timezone.localdate()).select_related('paciente','medico')
    return render(request,'dashboard/index.html',ctx)
@login_required
def historial(request,pk):
    paciente=get_object_or_404(Paciente,pk=pk); u=request.user
    medico=getattr(u,'perfil_medico',None)
    if not (u.is_superuser or getattr(getattr(u,'perfil_paciente',None),'pk',None)==pk or (medico and u.has_perm('pacientes.ver_historial_clinico'))):
        return HttpResponseForbidden('No autorizado.')
    return render(request,'pacientes/historial.html',{'paciente':paciente,'consultas':paciente.consultas.select_related('medico','cita')})

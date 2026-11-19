from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from .forms import CitaForm, ConsultaForm
from .models import Cita,ConsultaMedica,NotaConsulta
from pacientes.models import Paciente

def _can(user, permission, groups=()):
    return user.is_superuser or user.has_perm(permission) or user.groups.filter(name__in=groups).exists()

@login_required
def crear(request):
    user=request.user
    allowed=_can(user,'citas.add_cita',('Admins','Recepcionistas')) or (hasattr(user,'perfil_paciente') and user.has_perm('pacientes.agendar_cita'))
    if not allowed: return HttpResponseForbidden('No autorizado.')
    form=CitaForm(request.POST or None,user=user)
    if request.method=='POST' and form.is_valid():
        form.user=request.user
        try: form.save(); messages.success(request,'Cita agendada correctamente.'); return redirect('dashboard')
        except ValidationError as exc: form.add_error(None,exc)
    return render(request,'citas/form.html',{'form':form})

@login_required
@require_POST
def cancelar(request,pk):
    cita=get_object_or_404(Cita,pk=pk)
    own_patient=getattr(getattr(request.user,'perfil_paciente',None),'pk',None)==cita.paciente_id
    own_doctor=getattr(getattr(request.user,'perfil_medico',None),'pk',None)==cita.medico_id
    allowed=own_patient or own_doctor or _can(request.user,'citas.change_cita',('Admins','Recepcionistas'))
    if not allowed or not _can(request.user,'pacientes.cancelar_cita',('Admins','Recepcionistas','Médicos','Pacientes')) and not own_patient:
        return HttpResponseForbidden('No autorizado.')
    if cita.estado != Cita.Estado.PROGRAMADA:
        messages.error(request,'Solo se pueden cancelar citas programadas.')
    else:
        cita.estado=Cita.Estado.CANCELADA
        cita.save(update_fields=['estado'])
        messages.success(request,'Cita cancelada.')
    return redirect('dashboard')

@login_required
def disponibilidad(request):
    if not (_can(request.user,'citas.view_cita',('Admins','Recepcionistas','Médicos')) or hasattr(request.user,'perfil_paciente')):
        return HttpResponseForbidden('No autorizado.')
    citas=Cita.objects.filter(fecha__gte=date.today(),estado=Cita.Estado.PROGRAMADA).select_related('medico','especialidad').order_by('fecha','hora')
    return render(request,'citas/disponibilidad.html',{'citas':citas})

@login_required
def registrar_consulta(request,pk):
    cita=get_object_or_404(Cita.objects.select_related('medico','paciente'),pk=pk)
    doctor=getattr(request.user,'perfil_medico',None)
    if not doctor or doctor.pk!=cita.medico_id or not request.user.has_perm('citas.add_consultamedica'):
        return HttpResponseForbidden('No autorizado.')
    if cita.estado != Cita.Estado.PROGRAMADA or hasattr(cita,'consulta'):
        return HttpResponseForbidden('La cita no admite registro clínico.')
    if request.method=='POST':
        form=ConsultaForm(request.POST)
        if form.is_valid():
            consulta=form.save(commit=False)
            consulta.cita=cita; consulta.paciente=cita.paciente; consulta.medico=doctor
            consulta.save()
            cita.estado=Cita.Estado.COMPLETADA; cita.save(update_fields=['estado'])
            messages.success(request,'Consulta registrada.')
            return redirect('historial',pk=cita.paciente_id)
    else:
        form=ConsultaForm()
    return render(request,'citas/consulta_form.html',{'form':form,'cita':cita})

@login_required
@require_POST
def agregar_nota(request,pk):
    consulta=get_object_or_404(ConsultaMedica.objects.select_related('medico'),pk=pk)
    doctor=getattr(request.user,'perfil_medico',None)
    if not doctor or doctor.pk!=consulta.medico_id or not request.user.has_perm('citas.add_notaconsulta'):
        return HttpResponseForbidden('No autorizado.')
    texto=request.POST.get('texto','').strip()
    if not texto: messages.error(request,'La nota no puede estar vacía.')
    else:
        NotaConsulta.objects.create(consulta=consulta,autor=request.user,texto=texto)
        messages.success(request,'Nota posterior agregada.')
    return redirect('historial',pk=consulta.paciente_id)

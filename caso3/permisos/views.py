from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import render,redirect,get_object_or_404
from auditoria.models import Notificacion
from .models import Permiso
class SolicitudForm(forms.ModelForm):
    class Meta:
        model=Permiso; fields=['tipo','fecha_inicio','fecha_fin','motivo','documento_descripcion']; widgets={'fecha_inicio':forms.DateInput(attrs={'type':'date'}),'fecha_fin':forms.DateInput(attrs={'type':'date'})}
@login_required
def solicitar(request):
    if not hasattr(request.user,'empleado'): return HttpResponseForbidden()
    form=SolicitudForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        p=form.save(commit=False);p.empleado=request.user.empleado
        try: p.full_clean();p.save();messages.success(request,'Solicitud registrada.');return redirect('mis_permisos')
        except ValidationError as e: form.add_error(None,e)
    return render(request,'permisos/form.html',{'form':form})
@login_required
def mis_permisos(request):
    if hasattr(request.user,'empleado'): qs=Permiso.objects.filter(empleado=request.user.empleado)
    elif request.user.groups.filter(name='Jefe de Área').exists(): qs=Permiso.objects.filter(empleado__area__jefe=request.user)
    elif request.user.is_superuser or request.user.groups.filter(name='Administrador RRHH').exists(): qs=Permiso.objects.all()
    else: qs=Permiso.objects.none()
    saldo=30-sum(p.dias for p in qs.filter(tipo='vacaciones',estado='aprobado')) if hasattr(request.user,'empleado') else None
    return render(request,'permisos/lista.html',{'permisos':qs,'saldo':saldo})
@login_required
def resolver(request,pk,estado):
    if request.method!='POST': return HttpResponseForbidden()
    p=get_object_or_404(Permiso,pk=pk)
    try:
        p.resolver(request.user,estado,request.POST.get('observaciones',''))
        Notificacion.objects.create(usuario=p.empleado.usuario,mensaje=f'Tu solicitud de {p.get_tipo_display()} fue {estado}.')
        messages.success(request,'Solicitud actualizada y empleado notificado.')
    except ValidationError as e: messages.error(request,' '.join(e.messages))
    return redirect('mis_permisos')

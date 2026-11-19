from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Equipo, Prestamo, Laboratorio, Categoria, Auditoria
from .forms import PrestamoForm, DevolucionForm

def es(*roles): return lambda u: u.is_superuser or u.groups.filter(name__in=roles).exists()
def catalogo(request):
    equipos=Equipo.objects.select_related('categoria','laboratorio').all(); q=request.GET.get('q','').strip()
    if q: equipos=equipos.filter(Q(nombre__icontains=q)|Q(codigo_patrimonial__icontains=q))
    lab=request.GET.get('laboratorio'); cat=request.GET.get('categoria')
    if lab: equipos=equipos.filter(laboratorio_id=lab)
    if cat: equipos=equipos.filter(categoria_id=cat)
    return render(request,'equipos/catalogo.html',{'equipos':equipos,'laboratorios':Laboratorio.objects.all(),'categorias':Categoria.objects.all()})
@login_required
def dashboard(request):
    if request.user.is_superuser or es('Administrador')(request.user):
        return render(request,'dashboard/index.html',{'equipos':Equipo.objects.count(),'disponibles':Equipo.objects.filter(estado='operativo').count(),'mantenimiento':Equipo.objects.filter(estado='mantenimiento').count(),'activos':Prestamo.objects.filter(estado='activo').count(),'vencidos':Prestamo.objects.filter(estado='vencido').count(),'prestamos':Prestamo.objects.select_related('docente','equipo')[:8]})
    mine=Prestamo.objects.select_related('equipo').filter(docente=request.user)
    return render(request,'dashboard/index.html',{'prestamos':mine,'vencidos':getattr(request,'prestamos_vencidos',0),'prestamos_vencidos':getattr(request,'prestamos_vencidos',0)})
@login_required
@user_passes_test(es('Docente','Asistente','Administrador'))
def solicitar(request):
    if request.method=='POST':
        form=PrestamoForm(request.POST,usuario=request.user)
        if form.is_valid():
            with transaction.atomic():
                equipo=Equipo.objects.select_for_update().get(pk=form.cleaned_data['equipo'].pk)
                if equipo.estado!='operativo' or form.cleaned_data['cantidad']>equipo.stock_disponible:
                    form.add_error('equipo','La disponibilidad cambió; revise el equipo seleccionado.')
                else:
                    p=form.save(commit=False); p.docente=request.user; p.estado=Prestamo.Estado.ACTIVO if es('Asistente','Administrador')(request.user) else Prestamo.Estado.SOLICITADO; p.asistente=request.user if p.estado=='activo' else None; p.save(); messages.success(request,'Solicitud registrada correctamente.'); return redirect('dashboard')
    else: form=PrestamoForm(usuario=request.user)
    return render(request,'prestamos/form.html',{'form':form,'titulo':'Solicitar préstamo'})
@login_required
@user_passes_test(es('Asistente','Administrador'))
def devolver(request,pk):
    p=get_object_or_404(Prestamo.objects.select_related('equipo'),pk=pk)
    if p.estado not in ('activo','vencido'): messages.error(request,'Este préstamo ya no admite devolución.'); return redirect('dashboard')
    form=DevolucionForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            p=Prestamo.objects.select_for_update().get(pk=pk)
            if p.estado not in ('activo','vencido'): form.add_error(None,'El préstamo ya fue devuelto.')
            else:
                p.estado='devuelto'; p.fecha_real_devolucion=form.cleaned_data['fecha_real_devolucion']; p.asistente=request.user; p.observaciones=(p.observaciones+' '+form.cleaned_data['observaciones']).strip(); p.save()
                if form.cleaned_data['estado_equipo']!='operativo': p.equipo.estado='mantenimiento'; p.equipo.save(update_fields=['estado'])
                messages.success(request,'Devolución registrada.'); return redirect('dashboard')
    return render(request,'prestamos/form.html',{'form':form,'titulo':f'Devolución: {p.equipo}'})
@login_required
@user_passes_test(es('Administrador'))
def auditoria(request): return render(request,'dashboard/auditoria.html',{'eventos':Auditoria.objects.select_related('usuario')[:200]})

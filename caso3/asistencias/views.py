from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Asistencia
from .services import marcar_entrada,marcar_salida
@login_required
def marcar(request,accion):
    if request.method!='POST': return HttpResponseForbidden()
    if not hasattr(request.user,'empleado'): return HttpResponseForbidden('Cuenta sin ficha de empleado.')
    try:
        item=(marcar_entrada if accion=='entrada' else marcar_salida)(request.user.empleado)
        messages.success(request,f'Marcación de {accion} registrada: {timezone.localtime().strftime("%H:%M")}')
    except ValidationError as e: messages.error(request,' '.join(e.messages))
    return redirect('dashboard')
@login_required
def historial(request):
    qs=Asistencia.objects.select_related('empleado','empleado__area')
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['Administrador RRHH','Contador']).exists()):
        if request.user.groups.filter(name='Jefe de Área').exists(): qs=qs.filter(empleado__area__jefe=request.user)
        else: qs=qs.filter(empleado__usuario=request.user)
    return render(request,'asistencias/lista.html',{'asistencias':qs[:200]})
@login_required
def exportar(request):
    if not (request.user.is_superuser or request.user.groups.filter(name__in=['Administrador RRHH','Contador']).exists()): return HttpResponseForbidden()
    response=HttpResponse('Fecha\tDNI\tEmpleado\tÁrea\tEntrada\tSalida\tHoras\tExtras\n',content_type='text/plain; charset=utf-8');response['Content-Disposition']='attachment; filename="asistencia.txt"'
    for a in Asistencia.objects.select_related('empleado','empleado__area'):
        response.write(f'{a.fecha}\t{a.empleado.dni}\t{a.empleado.nombre_completo}\t{a.empleado.area}\t{a.hora_entrada or ""}\t{a.hora_salida or ""}\t{a.horas_trabajadas}\t{a.horas_extras}\n')
    return response

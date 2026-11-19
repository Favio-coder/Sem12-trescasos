from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Empleado
@login_required
def listado(request):
    try: area=request.user.empleado.area
    except Exception: area=None
    qs=Empleado.objects.select_related('area')
    if not (request.user.is_superuser or request.user.groups.filter(name='Administrador RRHH').exists()):
        if request.user.groups.filter(name='Jefe de Área').exists() and area: qs=qs.filter(area=area)
        else: qs=qs.filter(usuario=request.user)
    return render(request,'empleados/lista.html',{'empleados':qs})

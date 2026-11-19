from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
@login_required
@require_POST
def salir(request): logout(request); return redirect('catalogo')

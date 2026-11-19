from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Asistencia

def validar_horario(empleado, ahora):
    inicio=datetime.combine(ahora.date(),empleado.area.hora_entrada).replace(tzinfo=timezone.get_current_timezone())
    fin=datetime.combine(ahora.date(),empleado.area.hora_salida).replace(tzinfo=timezone.get_current_timezone())
    if ahora < inicio-timedelta(hours=2) or ahora > fin+timedelta(hours=2): raise ValidationError('Marcación fuera del horario permitido (±2 horas).')

def marcar_entrada(empleado, ahora=None):
    ahora=ahora or timezone.localtime()
    validar_horario(empleado,ahora)
    with transaction.atomic():
        if Asistencia.objects.select_for_update().filter(empleado=empleado,fecha=ahora.date(),hora_entrada__isnull=False).exists(): raise ValidationError('Ya existe una entrada registrada hoy.')
        item,created=Asistencia.objects.get_or_create(empleado=empleado,fecha=ahora.date(),defaults={'hora_entrada':ahora.time().replace(tzinfo=None)})
        if not created: raise ValidationError('Ya existe una marcación hoy.')
        item.save();return item

def marcar_salida(empleado, ahora=None):
    ahora=ahora or timezone.localtime()
    validar_horario(empleado,ahora)
    with transaction.atomic():
        item=Asistencia.objects.select_for_update().filter(empleado=empleado,fecha=ahora.date(),hora_entrada__isnull=False,hora_salida__isnull=True).first()
        if not item: raise ValidationError('No hay una entrada abierta para hoy.')
        item.hora_salida=ahora.time().replace(tzinfo=None);item.save();return item

from datetime import datetime, time, timedelta
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from empleados.models import Empleado

class Asistencia(models.Model):
    PRESENTE='presente'; TARDANZA='tardanza'; INCOMPLETO='incompleto'; JUSTIFICADO='justificado'
    ESTADOS=[(PRESENTE,'Presente'),(TARDANZA,'Tardanza'),(INCOMPLETO,'Incompleto'),(JUSTIFICADO,'Justificado')]
    empleado=models.ForeignKey(Empleado,on_delete=models.CASCADE,related_name='asistencias')
    fecha=models.DateField(default=timezone.localdate)
    hora_entrada=models.TimeField(null=True,blank=True); hora_salida=models.TimeField(null=True,blank=True)
    horas_trabajadas=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    horas_extras=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    estado=models.CharField(max_length=15,choices=ESTADOS,default=INCOMPLETO)
    observaciones=models.TextField(blank=True)
    creado=models.DateTimeField(auto_now_add=True); actualizado=models.DateTimeField(auto_now=True)
    class Meta: constraints=[models.UniqueConstraint(fields=['empleado','fecha'],name='asistencia_unica_empleado_fecha')]; ordering=['-fecha']
    def calcular(self):
        if self.hora_entrada and self.hora_salida:
            segundos=(datetime.combine(self.fecha,self.hora_salida)-datetime.combine(self.fecha,self.hora_entrada)).total_seconds()
            if segundos<=0: raise ValidationError('La salida debe ser posterior a la entrada y dentro del mismo día.')
            horas=Decimal(str(segundos/3600)).quantize(Decimal('0.01'))
            self.horas_trabajadas=horas; self.horas_extras=max(Decimal('0'),horas-Decimal('8')); self.estado=self.PRESENTE
        elif self.hora_entrada: self.estado=self.INCOMPLETO
    def save(self,*args,**kwargs): self.calcular(); super().save(*args,**kwargs)

class CorreccionAsistencia(models.Model):
    asistencia=models.ForeignKey(Asistencia,on_delete=models.CASCADE,related_name='correcciones')
    responsable=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    motivo=models.CharField(max_length=40,choices=[('error_sistema','Error del sistema'),('olvido','Olvido de marcación'),('otro','Otro')])
    justificacion=models.TextField()
    valores_anteriores=models.JSONField(); valores_nuevos=models.JSONField()
    fecha_hora=models.DateTimeField(auto_now_add=True)
    def clean(self):
        if len(self.justificacion.strip())<50: raise ValidationError({'justificacion':'La justificación debe tener al menos 50 caracteres.'})

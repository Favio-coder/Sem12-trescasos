from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from empleados.models import Empleado

class Permiso(models.Model):
    TIPOS=[('personal','Personal'),('medico','Médico'),('duelo','Duelo'),('maternidad','Maternidad/paternidad'),('otro','Otro'),('vacaciones','Vacaciones')]
    ESTADOS=[('pendiente','Pendiente'),('aprobado','Aprobado'),('rechazado','Rechazado')]
    empleado=models.ForeignKey(Empleado,on_delete=models.CASCADE,related_name='permisos')
    tipo=models.CharField(max_length=15,choices=TIPOS); fecha_inicio=models.DateField(); fecha_fin=models.DateField()
    motivo=models.TextField(); documento_descripcion=models.CharField(max_length=250,blank=True)
    estado=models.CharField(max_length=12,choices=ESTADOS,default='pendiente')
    aprobador=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='permisos_resueltos')
    fecha_aprobacion=models.DateTimeField(null=True,blank=True); observaciones_aprobacion=models.TextField(blank=True)
    creado=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-creado']; permissions=[('solicitar_permiso','Puede solicitar permisos'),('aprobar_permiso','Puede aprobar permisos')]
    @property
    def dias(self): return (self.fecha_fin-self.fecha_inicio).days+1
    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin<self.fecha_inicio: raise ValidationError({'fecha_fin':'Debe ser igual o posterior al inicio.'})
        if len(self.motivo.strip())<30: raise ValidationError({'motivo':'El motivo debe tener al menos 30 caracteres.'})
        if self.empleado_id and self.fecha_inicio and self.fecha_fin and Permiso.objects.filter(empleado=self.empleado,fecha_inicio__lte=self.fecha_fin,fecha_fin__gte=self.fecha_inicio).exclude(pk=self.pk).exists(): raise ValidationError('Las fechas se superponen con otra solicitud.')
        if self.tipo=='vacaciones' and self.empleado_id and self.estado=='pendiente':
            used=sum(p.dias for p in Permiso.objects.filter(empleado=self.empleado,tipo='vacaciones',estado='aprobado').exclude(pk=self.pk))
            if self.dias>30-used: raise ValidationError('La solicitud supera los días de vacaciones disponibles.')
    def resolver(self, usuario, estado, observaciones=''):
        with transaction.atomic():
            p=Permiso.objects.select_for_update().select_related('empleado__area').get(pk=self.pk)
            if p.estado!='pendiente': raise ValidationError('La solicitud ya fue resuelta.')
            es_rrhh=usuario.is_superuser or usuario.groups.filter(name='Administrador RRHH').exists()
            es_jefe=usuario.groups.filter(name='Jefe de Área').exists() and p.empleado.area.jefe_id==usuario.id
            if not (es_rrhh or es_jefe): raise ValidationError('No tiene autorización para resolver esta solicitud.')
            if estado not in ('aprobado','rechazado'): raise ValidationError('Estado no permitido.')
            if estado=='aprobado' and p.tipo=='vacaciones':
                usado=sum(x.dias for x in Permiso.objects.filter(empleado=p.empleado,tipo='vacaciones',estado='aprobado'))
                if p.dias>30-usado: raise ValidationError('Saldo de vacaciones insuficiente.')
            p.estado=estado;p.aprobador=usuario;p.fecha_aprobacion=timezone.now();p.observaciones_aprobacion=observaciones;p.save(update_fields=['estado','aprobador','fecha_aprobacion','observaciones_aprobacion']);return p

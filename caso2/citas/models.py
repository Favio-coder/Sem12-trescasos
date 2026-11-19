from django.conf import settings
from django.db import models


class Cita(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADA='programada','Programada'; COMPLETADA='completada','Completada'; CANCELADA='cancelada','Cancelada'; AUSENTE='ausente','Ausente'
    paciente=models.ForeignKey('pacientes.Paciente',on_delete=models.PROTECT,related_name='citas'); medico=models.ForeignKey('medicos.Medico',on_delete=models.PROTECT,related_name='citas'); especialidad=models.ForeignKey('medicos.Especialidad',on_delete=models.PROTECT); fecha=models.DateField(); hora=models.TimeField(); duracion_minutos=models.PositiveSmallIntegerField(default=30); motivo=models.CharField(max_length=500); estado=models.CharField(max_length=12,choices=Estado.choices,default=Estado.PROGRAMADA); creada=models.DateTimeField(auto_now_add=True); registrada_por=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,on_delete=models.SET_NULL,related_name='citas_registradas')
    class Meta:
        ordering=['fecha','hora']
        indexes=[models.Index(fields=['medico','fecha','hora']),models.Index(fields=['paciente','fecha'])]
        constraints=[
            models.CheckConstraint(condition=models.Q(duracion_minutos__gt=0),name='cita_duracion_positiva'),
            models.UniqueConstraint(fields=['paciente','fecha'],condition=models.Q(estado='programada'),name='una_cita_programada_paciente_dia'),
        ]
    def __str__(self): return f'{self.fecha} {self.hora} - {self.paciente}'
class ConsultaMedica(models.Model):
    cita=models.OneToOneField(Cita,on_delete=models.PROTECT,related_name='consulta'); paciente=models.ForeignKey('pacientes.Paciente',on_delete=models.PROTECT,related_name='consultas'); medico=models.ForeignKey('medicos.Medico',on_delete=models.PROTECT,related_name='consultas'); diagnostico=models.TextField(); tratamiento=models.TextField(); medicamentos=models.TextField(blank=True); proximo_control=models.DateField(null=True,blank=True); referencias_recetas=models.TextField(blank=True); referencias_examenes=models.TextField(blank=True); atendida_en=models.DateTimeField(auto_now_add=True); observaciones=models.TextField(blank=True)
    def save(self,*args,**kwargs):
        if self.pk:
            from django.core.exceptions import ValidationError
            raise ValidationError('El contenido clínico es inmutable; agregue una nota posterior.')
        super().save(*args,**kwargs)
    def delete(self,*args,**kwargs):
        from django.core.exceptions import ValidationError
        raise ValidationError('No se pueden eliminar registros clínicos.')
class NotaConsulta(models.Model):
    consulta=models.ForeignKey(ConsultaMedica,on_delete=models.CASCADE,related_name='notas'); autor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT); texto=models.TextField(); creada=models.DateTimeField(auto_now_add=True)
    def save(self,*args,**kwargs):
        from django.core.exceptions import ValidationError
        if self.pk:
            raise ValidationError('Las notas clínicas existentes no se pueden modificar.')
        super().save(*args,**kwargs)
    def delete(self,*args,**kwargs):
        from django.core.exceptions import ValidationError
        raise ValidationError('No se pueden eliminar notas clínicas.')

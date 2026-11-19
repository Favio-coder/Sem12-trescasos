from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
class Especialidad(models.Model):
    nombre=models.CharField(max_length=100, unique=True); descripcion=models.TextField(blank=True); activa=models.BooleanField(default=True)
    def __str__(self): return self.nombre
class Medico(models.Model):
    nombres=models.CharField(max_length=100); apellidos=models.CharField(max_length=100); cmp=models.CharField(max_length=5,unique=True,validators=[RegexValidator(r'^\d{5}$','El CMP debe tener cinco dígitos.')]); especialidad=models.ForeignKey(Especialidad,on_delete=models.PROTECT,related_name='medicos'); consultorio=models.CharField(max_length=50); usuario=models.OneToOneField(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='perfil_medico'); activo=models.BooleanField(default=True)
    def __str__(self): return f'Dr. {self.nombres} {self.apellidos}'
class HorarioMedico(models.Model):
    DIAS=[(0,'Lunes'),(1,'Martes'),(2,'Miércoles'),(3,'Jueves'),(4,'Viernes'),(5,'Sábado'),(6,'Domingo')]
    medico=models.ForeignKey(Medico,on_delete=models.CASCADE,related_name='horarios'); dia_semana=models.IntegerField(choices=DIAS); hora_inicio=models.TimeField(); hora_fin=models.TimeField(); consultorio=models.CharField(max_length=50)
    class Meta: ordering=['dia_semana','hora_inicio']; constraints=[models.CheckConstraint(condition=models.Q(hora_inicio__lt=models.F('hora_fin')),name='horario_inicio_antes_fin')]

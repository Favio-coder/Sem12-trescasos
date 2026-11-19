from datetime import date, time
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

class Area(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    jefe = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='areas_a_cargo')
    activa = models.BooleanField(default=True)
    hora_entrada = models.TimeField(default=time(9, 0))
    hora_salida = models.TimeField(default=time(18, 0))
    def __str__(self): return self.nombre

class Empleado(models.Model):
    PLANILLA='planilla'; LOCACION='locacion'
    dni = models.CharField(max_length=8, unique=True, validators=[RegexValidator(r'^\d{8}$','El DNI debe tener 8 dígitos.')])
    nombres = models.CharField(max_length=100); apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, related_name='empleados')
    fecha_ingreso = models.DateField()
    tipo_contrato = models.CharField(max_length=12, choices=[(PLANILLA,'Planilla'),(LOCACION,'Locación')], default=PLANILLA)
    correo = models.EmailField(unique=True)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='empleado')
    activo = models.BooleanField(default=True)
    saldo_vacaciones = models.PositiveSmallIntegerField(default=30)
    class Meta: ordering=['apellidos','nombres']; permissions=[('ver_reportes_area','Puede ver reportes de su área'),('ver_reportes_globales','Puede ver reportes globales')]
    def clean(self):
        super().clean()
        if self.fecha_ingreso and self.fecha_ingreso > date.today(): raise ValidationError({'fecha_ingreso':'La fecha de ingreso no puede ser futura.'})
        if self.correo and not self.correo.lower().endswith('@tecnoandes.pe'): raise ValidationError({'correo':'Use el dominio @tecnoandes.pe.'})
        if not self.cargo.strip(): raise ValidationError({'cargo':'El cargo es obligatorio.'})
    @property
    def nombre_completo(self): return f'{self.nombres} {self.apellidos}'
    @property
    def antiguedad(self):
        delta=date.today()-self.fecha_ingreso
        years=delta.days//365; months=(delta.days%365)//30
        return f'{years} años, {months} meses'
    def __str__(self): return self.nombre_completo

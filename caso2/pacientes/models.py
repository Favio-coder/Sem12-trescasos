from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

class Paciente(models.Model):
    class Tipo(models.TextChoices):
        ESTUDIANTE = 'estudiante', 'Estudiante'
        DOCENTE = 'docente', 'Docente'
    dni = models.CharField(max_length=8, unique=True, validators=[RegexValidator(r'^\d{8}$', 'El DNI debe tener exactamente 8 dígitos.')])
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    codigo_institucional = models.CharField(max_length=30, blank=True)
    email = models.EmailField()
    alergias = models.TextField(blank=True)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='perfil_paciente')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    class Meta:
        permissions = [('ver_historial_clinico', 'Puede ver historial clínico'), ('agendar_cita', 'Puede agendar cita'), ('cancelar_cita', 'Puede cancelar cita'), ('generar_reportes', 'Puede generar reportes')]
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_nacimiento and self.fecha_nacimiento > timezone.localdate(): raise ValidationError({'fecha_nacimiento':'La fecha no puede ser futura.'})
        if self.tipo == self.Tipo.ESTUDIANTE and not self.email.lower().endswith('@uncp.edu.pe'): raise ValidationError({'email':'El estudiante debe usar correo @uncp.edu.pe.'})
    def __str__(self): return f'{self.apellidos}, {self.nombres} ({self.dni})'

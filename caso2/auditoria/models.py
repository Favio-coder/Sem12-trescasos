from django.conf import settings
from django.db import models
class AuditoriaMedica(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL); paciente=models.ForeignKey('pacientes.Paciente',null=True,blank=True,on_delete=models.SET_NULL); recurso=models.CharField(max_length=200); accion=models.CharField(max_length=30); fecha_hora=models.DateTimeField(auto_now_add=True); ip=models.GenericIPAddressField(null=True,blank=True); resultado=models.CharField(max_length=20)
    class Meta: ordering=['-fecha_hora']
    def __str__(self): return f'{self.fecha_hora}: {self.accion} {self.recurso} ({self.resultado})'

from django.conf import settings
from django.db import models
class Auditoria(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    accion=models.CharField(max_length=40); recurso=models.CharField(max_length=100); registro_id=models.CharField(max_length=80)
    fecha_hora=models.DateTimeField(auto_now_add=True); ip=models.GenericIPAddressField(null=True,blank=True); descripcion=models.TextField(blank=True)
    class Meta: ordering=['-fecha_hora']
class Notificacion(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='notificaciones')
    mensaje=models.CharField(max_length=250); creada=models.DateTimeField(auto_now_add=True); leida=models.BooleanField(default=False)

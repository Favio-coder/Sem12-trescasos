from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class Laboratorio(models.Model):
    nombre = models.CharField(max_length=120)
    codigo = models.CharField(max_length=20, unique=True)
    ubicacion = models.CharField(max_length=160)
    descripcion = models.TextField(blank=True)
    def __str__(self): return f'{self.codigo} - {self.nombre}'

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    def __str__(self): return self.nombre

class Equipo(models.Model):
    class Estado(models.TextChoices):
        OPERATIVO='operativo','Operativo'; MANTENIMIENTO='mantenimiento','Mantenimiento'; BAJA='baja','Baja'
    codigo_patrimonial=models.CharField(max_length=40,unique=True)
    nombre=models.CharField(max_length=120); marca=models.CharField(max_length=80,blank=True); modelo=models.CharField(max_length=80,blank=True)
    categoria=models.ForeignKey(Categoria,on_delete=models.PROTECT,related_name='equipos')
    laboratorio=models.ForeignKey(Laboratorio,on_delete=models.PROTECT,related_name='equipos')
    estado=models.CharField(max_length=20,choices=Estado.choices,default=Estado.OPERATIVO)
    stock_total=models.PositiveIntegerField(default=1,validators=[MinValueValidator(1)])
    ultimo_mantenimiento=models.DateField(null=True,blank=True)
    fecha_registro=models.DateTimeField(auto_now_add=True)
    @property
    def dias_desde_mantenimiento(self): return (timezone.localdate()-self.ultimo_mantenimiento).days if self.ultimo_mantenimiento else None
    @property
    def stock_disponible(self):
        n=self.prestamos.filter(estado__in=[Prestamo.Estado.ACTIVO,Prestamo.Estado.VENCIDO]).aggregate(n=models.Sum('cantidad'))['n'] or 0
        return max(0,self.stock_total-n)
    def __str__(self): return f'{self.codigo_patrimonial} - {self.nombre}'

class Prestamo(models.Model):
    class Estado(models.TextChoices):
        SOLICITADO='solicitado','Solicitado'; ACTIVO='activo','Activo'; DEVUELTO='devuelto','Devuelto'; VENCIDO='vencido','Vencido'; RECHAZADO='rechazado','Rechazado'
    docente=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='prestamos')
    equipo=models.ForeignKey(Equipo,on_delete=models.PROTECT,related_name='prestamos')
    cantidad=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    fecha_prestamo=models.DateField(default=timezone.localdate)
    fecha_prevista_devolucion=models.DateField()
    fecha_real_devolucion=models.DateField(null=True,blank=True)
    estado=models.CharField(max_length=20,choices=Estado.choices,default=Estado.SOLICITADO)
    observaciones=models.CharField(max_length=500,blank=True)
    asistente=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='prestamos_atendidos')
    @property
    def dias_retraso(self):
        if self.estado not in (self.Estado.ACTIVO,self.Estado.VENCIDO): return 0
        return max(0,(timezone.localdate()-self.fecha_prevista_devolucion).days)
    def __str__(self): return f'{self.docente} / {self.equipo}'

class Auditoria(models.Model):
    usuario=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    accion=models.CharField(max_length=50); fecha_hora=models.DateTimeField(auto_now_add=True); direccion_ip=models.GenericIPAddressField(null=True,blank=True)
    recurso=models.CharField(max_length=120); descripcion=models.TextField(blank=True)
    class Meta: ordering=['-fecha_hora']
    def __str__(self): return f'{self.accion}: {self.recurso}'

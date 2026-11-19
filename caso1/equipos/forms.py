from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Equipo, Prestamo

class PrestamoForm(forms.ModelForm):
    class Meta:
        model=Prestamo; fields=['equipo','cantidad','fecha_prestamo','fecha_prevista_devolucion','observaciones']
        widgets={'fecha_prestamo':forms.DateInput(attrs={'type':'date'}),'fecha_prevista_devolucion':forms.DateInput(attrs={'type':'date'}),'observaciones':forms.Textarea(attrs={'rows':3,'maxlength':500})}
    def __init__(self,*args,usuario=None,**kwargs): super().__init__(*args,**kwargs); self.usuario=usuario
    def clean_cantidad(self):
        n=self.cleaned_data['cantidad']
        if n<=0: raise ValidationError('La cantidad debe ser mayor que cero.')
        return n
    def clean_observaciones(self): return ' '.join(self.cleaned_data.get('observaciones','').split())
    def clean(self):
        d=super().clean(); equipo=d.get('equipo')
        if d.get('fecha_prevista_devolucion') and d.get('fecha_prestamo') and d['fecha_prevista_devolucion']<=d['fecha_prestamo']: self.add_error('fecha_prevista_devolucion','Debe ser posterior a la fecha de préstamo.')
        if equipo:
            if equipo.estado!=Equipo.Estado.OPERATIVO: self.add_error('equipo','El equipo no está operativo.')
            if d.get('cantidad') and d['cantidad']>equipo.stock_disponible: self.add_error('cantidad',f'Stock disponible: {equipo.stock_disponible}.')
        if self.usuario and self.usuario.is_authenticated:
            activos=Prestamo.objects.filter(docente=self.usuario,estado__in=[Prestamo.Estado.ACTIVO,Prestamo.Estado.VENCIDO]).count()
            if activos>=3: raise ValidationError('No puede tener más de tres préstamos activos simultáneamente.')
        return d

class DevolucionForm(forms.Form):
    fecha_real_devolucion=forms.DateField(initial=timezone.localdate,widget=forms.DateInput(attrs={'type':'date'}))
    estado_equipo=forms.ChoiceField(choices=[(Equipo.Estado.OPERATIVO,'Operativo'),(Equipo.Estado.MANTENIMIENTO,'Mantenimiento')])
    observaciones=forms.CharField(required=False,max_length=500,widget=forms.Textarea(attrs={'rows':3}))
    def clean_observaciones(self): return ' '.join(self.cleaned_data.get('observaciones','').split())
